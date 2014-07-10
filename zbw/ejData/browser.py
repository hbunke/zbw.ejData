# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations


class CsvView(BrowserView):
    """
    csv view for article level metrics and data
    """

    template = ViewPageTemplateFile("csv.pt")


    def __call__(self):
        self.request.set('disable_border', True)
        self.request.response.setHeader("Content-type", "text/csv; charset=utf-8")
        self.request.response.setHeader("Content-Transfer-Encoding", "8bit")
        #return self.template()
        return self.csv()

    def csv(self):
        """
        """
        paper = self.context
        view = getMultiAdapter((paper, self.request), name='adata_common')
        paper_view = getMultiAdapter((paper, self.request), name='paperView')
        citation_view = getMultiAdapter((paper, self.request), name="citations")
        dp_ja = view.corr_ja()
        ja_dp = view.corr_dp()
        ja = view.is_ja()
        dp = view.is_dp()
        pdf_dates = view.pdf_dates()
        
        text = u""
        header = u"Paper Type; ID; "
        if ja:
            header += u"ID of corresponding DiscussionPaper; "
        if dp:
            header += u"ID of corresponding JournalArticle; "
        header += u" Date Submission; Date accepted as Discussion Paper; Date published as Discussion Paper;"
        if ja:
            header += u"Date of paper revision; Date accepted as Journal Article; Date published as Journal Article;"
        header += u"Title; Authors (Affiliation); JEL; Number of Downloads; Number of Comments; Number of Citations; Repec Handles of Citations; Policy Paper; Special Issues; Survey and Overview Paper; Number of Pages; "
        if ja:
            header += u"DOI of Journal Article; Handle/DOI of Data Set;"
        header += "\n"
        text += header
        
        text += u"%s; '%s'; " %(paper.portal_type, paper.getId())
        if ja and ja_dp:
            text += u"'%s'; " %ja_dp.getId()
        if dp:
            text += u"'%s'; " %dp_ja
        text += u"%s; " %pdf_dates['date_submission']
        text += u"%s; " %pdf_dates['date_accepted_as_dp']
        if dp:
            text += u"%s; " %view.published()
        if ja:
            dp = getMultiAdapter((ja_dp, self.request), name="adata_common")
            text += u"%s; " %dp.published()
            text += u"%s; " %pdf_dates['date_revised']
            text += u"%s; " %pdf_dates['date_accepted_as_ja']
            text += u"%s; " %view.published()

        text += u"'%s'; " %paper.Title()
        
        authors = paper.getAuthorsForTitle()
        for author in authors:
            text += u"'%s (%s)' " %(author.getFullname(), author.getOrganisation())
        text += u"; "
        
        commons = (
                view.clean_jels(),
                view.downloads(),
                paper_view.getAmountOfCommentsAsInteger(),
                citation_view.count(),
                view.citation_handles(),
                paper.isPolicyPaper,
                view.clean_special_issues(),
                paper.isSurveyAndOverviewPaper,
                paper.getPages(),
                )
        for i in commons:
            text += u"%s; " %i
        
        if ja:
            text += u"%s; " %view.get_doi()
            text += u"%s; " %paper_view.dataset_pi_url()
        
        return text


    
    
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




    

