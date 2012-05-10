#!/usr/bin/env python
import logging

from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from utils import LinkedinAPI, OpenErpAPI, get_config
from utils import create_update_contact

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# Extra fields
FIELDS = ['specialties','honors','skills', 'interests','summary', 'picture-url', 'public-profile-url', 'languages']

linkedin_info = get_config(
    "LINKEDIN_INFO",
    ["KEY", "SECRET", "USERNAME", "PASSWORD", "CALLBACK_EMPLOYEE", "CALLBACK_CONTACT"])
openerp_info = get_config(
    "OPENERP_INFO",
    ["HOST", "PORT", "DBNAME", "USER", "PASSWORD"])


linkedin_api = LinkedinAPI(
    linkedin_info['KEY'],
    linkedin_info['SECRET'])
 
# custom views
def home(request, template='home.html'):
    context = RequestContext(request, {})
    return render_to_response(template, context_instance=context)

def error(request, template='error.html'):
    context = RequestContext(request, {})
    return render_to_response(template, context_instance=context)

def linkedin_auth(request):
    """ LinkedIn auth process """

    logger.info("Linkedin Contact View")
    error_url = urlresolvers.reverse('error')
    logger.debug("POST")
    # linkedin_api.api._callback_url = linkedin_info['CALLBACK_CONTACT']
    linkedin_api.api._callback_url = "http://localhost:10000/auth/linkedin/company/"
    result = linkedin_api.request_token()
    if result == True:
        url = linkedin_api.get_authorize_url()
        logger.info("Linkedin URL %s" % url)
    else:
        logger.error("ERROR")
        return HttpResponseRedirect(error_url)

    return HttpResponseRedirect(url)

def linkedin_auth_empl(request):
    """ LinkedIn auth process """

    logger.info("Linkedin Contact View")
    error_url = urlresolvers.reverse('error')
    if request.GET:
        logger.info("----------------------------------")
        logger.info("GET")
        oauth_verifier = request.GET.get('oauth_verifier', '')
        logger.info("Linkedin Verifier code : %s" % oauth_verifier)
        access_token = linkedin_api.access_token(oauth_verifier)
        if access_token == True:
            employees = []
            try:
                openerp_api = OpenErpAPI(
                    openerp_info['HOST'],
                    openerp_info['PORT'],
                    openerp_info['DBNAME'],
                    openerp_info['USER'],
                    openerp_info['PASSWORD'])
                employees = openerp_api.search_employees()
            except Exception, e:
                logger.error("ERROR on OpenErp : %s" % e)
                return HttpResponseRedirect(error_url)

            logger.info(employees.__repr__())
            # Search employess on Linkedin
            for empl in employees:
                linkedin_item = linkedin_api.get_search({
                    'name': empl['name'].replace(' ', '+'),
                    'company': empl['company_id'][1]
                })
                linkedin_extra_info = []
                for item in linkedin_item:
                    linkedin_extra_info.append(linkedin_api.get_profile(member_id=item.id, fields=FIELDS))
                if len(linkedin_item) == 0:
                    logger.warning("No Profile found on Linkedin for : %s" % empl['name'])
                elif len(linkedin_item) > 1:
                    logger.warning("Too many profiles found on Linkedin for : %s" % empl['name'])
                    i=0
                    for item in linkedin_item:
                        openerp_api.update_backlog(empl, item, linkedin_extra_info[i], 'hr.employee')
                        i=i+1
                else:
                    logger.info("Update Linkedin info on OpenErp for : %s" % empl['name'])
                    # openerp_api.update_profile(empl, linkedin_item[0], linkedin_extra_info[0], 'hr.employee')
                    update_create_contact(empl, linkedin_item[0], linkedin_extra_info[0])
        else:
            logger.error("ERROR")
            return HttpResponseRedirect(error_url)
    return HttpResponseRedirect('/')

def linkedin_auth_cont(request):
    """ LinkedIn auth process """

    logger.info("Linkedin Contact View")
    error_url = urlresolvers.reverse('error')
    if request.GET:
        logger.info("----------------------------------")
        logger.info("GET")
        oauth_verifier = request.GET.get('oauth_verifier', '')
        logger.info("Linkedin Verifier code : %s" % oauth_verifier)
        access_token = linkedin_api.access_token(oauth_verifier)
        if access_token == True:
            import pdb;pdb.set_trace()
            linkedin_item = linkedin_api.get_search({ 'keywords': "{abstract}"})
            contacts = []
            try:
                openerp_api = OpenErpAPI(
                    openerp_info['HOST'],
                    openerp_info['PORT'],
                    openerp_info['DBNAME'],
                    openerp_info['USER'],
                    openerp_info['PASSWORD'])
                contacts = openerp_api.search_contacts()
            except Exception, e:
                logger.error("ERROR on OpenErp : %s" % e)
                return HttpResponseRedirect(error_url)

            logger.info(contacts.__repr__())
            # Search employess on Linkedin
            for empl in contacts:
                logger.info(empl.__repr__())
                if empl['last_name'] and empl['first_name'] and empl['partner_id']:
                    linkedin_item = linkedin_api.get_search({ 'name': empl['first_name'].replace(' ', '+') +'+'+ empl['last_name'].replace(' ', '+'), 'company': empl['partner_id'][1]})
                    linkedin_extra_info = []
                    for item in linkedin_item:
                        linkedin_extra_info.append(linkedin_api.get_profile(member_id=item.id, fields=FIELDS))
                    if len(linkedin_item) == 0:
                        logger.warning("No Profile found on Linkedin for : %s %s" % (empl['first_name'], empl['last_name']))
                    elif len(linkedin_item) > 1:
                        logger.warning("Too many profiles found on Linkedin for : %s %s" % (empl['first_name'], empl['last_name']))
                        i=0
                        for item in linkedin_item:
                            # openerp_api.update_backlog(empl, item, linkedin_extra_info[i], 'res.partner.contact')
                            logger.info("Update Linkedin info on OpenErp for : %s %s" % (empl['first_name'], empl['last_name']))
                            create_update_contact(item, linkedin_extra_info[i])
                            i=i+1
                    else:
                        logger.info("Update Linkedin info on OpenErp for : %s %s" % (empl['first_name'], empl['last_name']))
                        # openerp_api.update_profile(empl, linkedin_item[0], linkedin_extra_info[0], 'res.partner.contact')
                        create_update_contact(linkedin_item[0], linkedin_extra_info[0])
                else:
                    logger.warning("Not enough information")
        else:
            logger.error("ERROR")
            return HttpResponseRedirect(error_url)
    return HttpResponseRedirect('/')

def linkedin_auth_comp(request):
    """ LinkedIn auth process """

    logger.info("Linkedin Company View")
    error_url = urlresolvers.reverse('error')
    if request.GET:
        logger.info("----------------------------------")
        logger.info("GET")
        oauth_verifier = request.GET.get('oauth_verifier', '')
        logger.info("Linkedin Verifier code : %s" % oauth_verifier)
        access_token = linkedin_api.access_token(oauth_verifier)
        if access_token == True:
            import pdb;pdb.set_trace()
            linkedin_item = linkedin_api.get_company_search({ 'keywords': "{telecom italia}"})
        else:
            logger.error("ERROR")
            return HttpResponseRedirect(error_url)
    return HttpResponseRedirect('/')