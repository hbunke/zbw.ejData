# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
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

    def published_split(self):
        """
        """
        created = self.context.created()
        if created is not None:
            year = created.strftime("%Y")
            month = created.strftime("%B")
            day = created.strftime("%d")
            return (year, month, day)
        return (u"", u"", u"")
           

    def downloads(self):
        """
        """
        #XXX might add more sophisticated numbers for ja
        click_view = getMultiAdapter((self.context, self.request), name='clickView')
        return click_view.getClicks()


    def citation_handles(self, output='csv'):
        """
        """
        obj = self.context
        ann = IAnnotations(obj)
        
        try:
            citations = ann['zbw.citation']['repec']
            if output == 'csv':
                text = u""
                for cite in citations:
                    text += u"'%s', " %cite
                return text
            if output == 'json':
                return citations
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
            return rel
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

    
    def split_date(self, date):
        """
        helper method to split date *string* (not datetime object) from pdf
        cover dates
        """
        #date is expected like "Month Day, Year"
        #first check for empty string
        if not date:
            return (u"", u"", u"")
        date_split = date.split(',')
        year = date_split[1].lstrip()
        md = date_split[0].split()
        month = md[0]
        day = md[1]
        return (year, month, day)
        

    def get_clickdates(self):
        """
        get and format article download dates
        """

        ann = IAnnotations(self.context)
        clickdates = ann['hbxt.clickdates'].values()
        datelist = []
        for clickdate in clickdates:
            for date in clickdate:
                d = date.strftime('%x %X')
                datelist.append(d)
        
        return datelist


