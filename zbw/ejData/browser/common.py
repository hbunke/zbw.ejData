# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations



class View(BrowserView):
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
        click_view = getMultiAdapter((self.context, self.request), name='clickView')
        return click_view.getClicks()


    def citation_handles(self):
        """
        """
        obj = self.context
        ann = IAnnotations(obj)
        
        try:
            citations = ann['zbw.citation']['repec']
            text = u""
            for cite in citations:
                text += u"'%s', " %cite
            return text

        except:
            return None

    
    def get_doi(self):
        """
        """
        ja_view = getMultiAdapter((self.context, self.request), name="ja_view")
        doi = ja_view.get_doi()
        return doi
    

    def pdf_dates(self):
        """
        """
        pdf_view = getMultiAdapter((self.context, self.request), name="cover_control")
        ann = pdf_view.annotations()
        keys = ['date_submission', 'date_accepted_as_dp', 'date_revised', 'date_accepted_as_ja']
        dates = {}
        for key in keys:
            if key in ann.keys():
                dates[key] = ann[key]
            else:
                dates[key] = u""
        return dates

    
    def corr_dp(self):
        """
        """
        try:
            refs = self.context.getRefs('journalpaper_discussionpaper')[0]
            return refs
        except:
            return False
         

    def corr_ja(self):
        """
        """
        paper_view = getMultiAdapter((self.context, self.request),name="paperView")
        if paper_view.showRelatedJournalPaper():
            rel = self.context.getBRefs('journalpaper_discussionpaper')[0]
            return rel.getId()
        return False

    
    def is_ja(self):
        """
        helper method for checking portal type once
        """
        obj = self.context
        pt = obj.portal_type
        if pt != "JournalPaper":
            return False
        return True

    
    def is_dp(self):
        """
        helper method to avoid too much writing in portal type conditionals
        """
        obj = self.context
        pt = obj.portal_type
        if pt != "DiscussionPaper":
            return False
        return True

    def clean_jels(self):
        jels = self.context.getJel()
        text = u""
        for jel in jels:
            text += "%s," %jel
        return text
        
    def clean_special_issues(self):
        sis = self.context.getSpecialIssues()
        clean = u""
        for si in sis:
            clean += u"'%s'" %si
        return clean





