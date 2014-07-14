from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations



class View(BrowserView):
    """
    json view for article level metrics and data
    """
    
    #template = ViewPageTemplateFile("json.pt")


    def __call__(self):
        self.request.set('disable_border', True)
        #return self.template
        self.request.response.setHeader("Content-type", "text/csv; charset=utf-8")
        self.request.response.setHeader("Content-Transfer-Encoding", "8bit")
        #return self.template()
        return self.json()



