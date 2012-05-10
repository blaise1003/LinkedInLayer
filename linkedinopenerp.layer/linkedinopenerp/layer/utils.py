import mechanize
from linkedin import linkedin
from openerp.utils import rpc

from livesettings import config_value

from .models import Contact, Position


def get_config(group='', keys=[]):
    vocab = {}
    for key in keys:
        vocab[key] = config_value(group, key)
    return vocab


def normalize_value(value=''):
    if isinstance(value, list):
        value = ','.join(str(n) for n in value)
    return value or False


def get_linkedin_values(li_empl, li_extrainfo):
    values = {
        'profile_id': normalize_value(li_empl.id),
        'first_name': normalize_value(li_empl.first_name),
        'last_name': normalize_value(li_empl.last_name),
        'headline': normalize_value(li_empl.headline),
        'specialties': normalize_value(li_extrainfo.specialties),
        'industry': normalize_value(li_empl.industry),
        'honors': normalize_value(li_extrainfo.honors),
        'interests': normalize_value(li_extrainfo.interests),
        'languages': normalize_value(li_extrainfo.languages),
        'picture_url': normalize_value(li_extrainfo.picture_url),
        'skills': normalize_value(li_extrainfo.skills),
        'public_url': normalize_value(li_extrainfo.public_url),
        'location_country': normalize_value(li_empl.location_country),
        'location': normalize_value(li_empl.location)}
    return values


def get_pos_values(position):
    format = "%Y-%m-%d %H:%M:%S"

    if position.start_date is None:
        start_date = False
    else:
        start_date = position.start_date.strftime(format)

    if position.end_date is None:
        end_date = False
    else:
        end_date = position.end_date.strftime(format)

    pos_values = {
        'ref': normalize_value(position.id),
        'title': normalize_value(position.title),
        'summary': normalize_value(position.summary),
        'start_date': start_date,
        'end_date': end_date,
        'company': normalize_value(position.company)}
    return pos_values


def create_update_positions(contact, positions):
    c_pos = contact.position_set.all()
    refs = [x.ref for x in c_pos]
    for pos in positions:
        pos_values = get_pos_values(pos)
        if pos_values['ref'] in refs:
            position = c_pos.filter(ref=pos_values['ref']).all()[0]
        else:
            position = Position(contact=contact, ref=pos_values['ref'])
        position.update_values(pos_values)
        position.save()


def create_update_contact(li_empl, li_extrainfo):
    vals = get_linkedin_values(li_empl, li_extrainfo)
    cont = Contact.objects.filter(profile_id=vals['profile_id']).all()
    if not cont:
        contact = Contact(profile_id=vals['profile_id'])
    else:
        contact = cont[0]
    contact.update(vals)
    contact.save()
    create_update_positions(contact, li_empl.positions)


search_employee_fields = [
'name',
'company_id']


search_contact_fields = [
'last_name',
'first_name',
'partner_id']


class LinkedinAPI(object):
    """Linkedin API

    This class provides all the methods to create a
    coneection with linkedin and do search for people."""

    def __init__(self, key='', secret='', callback_url=''):
        self.api = linkedin.LinkedIn(key, secret, callback_url)

    def request_token(self):
        return self.api.request_token()

    def get_authorize_url(self):
        return self.api.get_authorize_url()

    def access_token(self, oauth_verifier=''):
        return self.api.access_token(verifier=oauth_verifier)

    def get_profile(self, member_id="", fields=[]):
        return self.api.get_profile(member_id=member_id, fields=fields)

    def get_connections(self):
        return self.api.get_connections()

    def get_search(self, params={}):
        return self.api.get_search(params)

    def get_company_search(self, params={}):
        return self.api.get_company_search(params)

    def fill_auth_form(self, url='', key='', password=''):
        br = mechanize.Browser()
        br.open(url)
        br.select_form(name="oauthAuthorizeForm")
        br["session_key"] = key
        br["session_password"] = password
        response = br.submit()
        return response


class OpenErpAPI(object):
    """OpenERP Connection

    This library is used to connect, search and write
    in openerp through xmlrpc calls."""

    format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, host='', port='', dbname='', user='', password=''):
        self.conn = rpc.Connection(dbname, user, password,
            'http://%s:%s/xmlrpc/common' % (host, port),
            'http://%s:%s/xmlrpc/object' % (host, port))

    def erpize_value(self, value=''):
        if isinstance(value, list):
            value = ','.join(str(n) for n in value)
        return value or False

    def search_employees(self):
        qargs = [('linkedin', '=', True)]
        employee_ids = self.conn.search('hr.employee', qargs)
        employees = self.conn.read('hr.employee', employee_ids,
                                            search_employee_fields)
        return employees

    def search_contacts(self):
        qargs = [
            ('linkedin', '=', True),
            ('name', '!=', ''),
            ('first_name', '!=', '')]
        contact_ids = self.conn.search('res.partner.contact', qargs)
        contacts = self.conn.read('res.partner.contact', contact_ids,
                                                    search_contact_fields)
        return contacts

    def search_position(self, pos_id=''):
        qargs = [('ref', '=', pos_id)]
        position_ids = self.conn.search('linkedin.position', qargs)
        positions = self.conn.read('linkedin.position', position_ids, ['id'])
        return positions

    def get_pos_values(self, empl_id, position, oe_object):
        if position.start_date is None:
            start_date = False
        else:
            start_date = position.start_date.strftime(self.format)

        if position.end_date is None:
            end_date = False
        else:
            end_date = position.end_date.strftime(self.format)

        pos_values = {
            'ref': self.erpize_value(position.id),
            'title': self.erpize_value(position.title),
            'summary': self.erpize_value(position.summary),
            'start_date': start_date,
            'end_date': end_date,
            'company': self.erpize_value(position.company),
        }
        if oe_object == 'hr.employee':
            pos_values['employee_id'] = self.erpize_value(empl_id)
        elif oe_object == 'res.partner.contact':
            pos_values['contact_id'] = self.erpize_value(empl_id)
        elif oe_object == 'linkedin.backlog':
            pos_values['backlog_id'] = self.erpize_value(empl_id)
        return pos_values

    def update_position(self, empl_id, pos_id, position, oe_object):
        pos_values = self.get_pos_values(empl_id, position, oe_object)
        try:
            self.conn.write('linkedin.position', [pos_id], pos_values)
        except Exception, e:
            print e

    def update_positions(self, employee, linkedin_positions=[],
                                                            oe_object=None):
        for pos in linkedin_positions:
            pos_id = pos.id
            pos_results = self.search_position(pos_id)
            if len(pos_results) > 1:
                return False

            if pos_results:
                pos_id = pos_results[0]
                self.update_position(employee['id'], pos_id['id'], pos,
                                                                oe_object)
            else:
                self.create_position(employee['id'], pos, oe_object)

    def create_position(self, empl_id, position, oe_object):
        pos_values = self.get_pos_values(empl_id, position, oe_object)
        try:
            self.conn.create('linkedin.position', pos_values)
        except Exception, e:
            print e

    def get_linkedin_values(self, li_empl, li_extrainfo):
        values = {
            'linkedin_profile_id': self.erpize_value(li_empl.id),
            'linkedin_first_name': self.erpize_value(li_empl.first_name),
            'linkedin_last_name': self.erpize_value(li_empl.last_name),
            'linkedin_headline': self.erpize_value(li_empl.headline),
            'linkedin_specialties': self.erpize_value(
                                                li_extrainfo.specialties),
            'linkedin_industry': self.erpize_value(li_empl.industry),
            'linkedin_honors': self.erpize_value(li_extrainfo.honors),
            'linkedin_interests': self.erpize_value(li_extrainfo.interests),
            'linkedin_languages': self.erpize_value(li_extrainfo.languages),
            'linkedin_picture_url': self.erpize_value(
                                                li_extrainfo.picture_url),
            'linkedin_skills': self.erpize_value(li_extrainfo.skills),
            'linkedin_public_url': self.erpize_value(li_extrainfo.public_url),
            'linkedin_location_country': self.erpize_value(
                                                li_empl.location_country),
            'linkedin_location': self.erpize_value(li_empl.location)}
        return values

    def update_profile(self, op_empl, li_empl, li_extrainfo, oe_object):
        if li_empl and li_extrainfo:
            values = self.get_linkedin_values(li_empl, li_extrainfo)
            try:
                self.conn.write(oe_object, [op_empl['id']], values)
            except Exception, e:
                print e

        # Update positions
        self.update_positions(op_empl, li_empl.positions, oe_object)

    def update_backlog(self, op_empl, li_empl, li_extrainfo, oe_object):
        if li_empl and li_extrainfo:
            values = self.get_linkedin_values(li_empl, li_extrainfo)
            if oe_object == 'hr.employee':
                values['employee_id'] = self.erpize_value(op_empl['id'])
            elif oe_object == 'res.partner.contact':
                values['contact_id'] = self.erpize_value(op_empl['id'])
            try:
                _id = self.conn.create('linkedin.backlog', values)
            except Exception, e:
                print e

            for pos in li_empl.positions:
                self.create_position(_id, pos, 'linkedin.backlog')
