# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


class CsvView(BrowserView):
    """
    csv view for article level metrics and data
    """

    template = ViewPageTemplateFile("csv.pt")


    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()



class JsonView(BrowserView):
    """
    json view for article level metrics and data
    """
    
    template = ViewPageTemplateFile("json.pt")


    def __call__(self):
        self.request.set('disable_border', True)
        return self.template



class CommonView(BrowserView):
    """
    common getters
    """

    def published(self):
        """
        """
        created = self.context.created()
        
        if created is not None:
            #TODO format time string 
            return created.strftime("%B %d, %Y")
        
        return "None"


    def downloads(self):
        """
        """
        #XXX might add more sophisticated numbers for ja
        pt = self.context.portal_type
        click_view = getMultiAdapter((self.context, self.request), name='clickView')
        return click_view.getClicks()





    

