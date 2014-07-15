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
    csv view for article level metrics and data
    """

    #template = ViewPageTemplateFile("csv.pt")


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
            text += u"'%s'; " %dp_ja.getId()
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
                self.clean_jels(),
                view.downloads(),
                paper_view.getAmountOfCommentsAsInteger(),
                citation_view.count(),
                view.citation_handles(),
                paper.isPolicyPaper,
                self.clean_special_issues(),
                paper.isSurveyAndOverviewPaper,
                paper.getPages(),
                )
        for i in commons:
            text += u"%s; " %i
        
        if ja:
            text += u"%s; " %view.get_doi()
            text += u"%s; " %paper_view.dataset_pi_url()
        
        return text


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

