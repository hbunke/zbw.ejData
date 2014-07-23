# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
#from zope.annotation.interfaces import IAnnotations


class View(BrowserView):
    """
    csv view for article level metrics and data
    """

    #template = ViewPageTemplateFile("csv.pt")


    def __call__(self):
        self.request.set('disable_border', True)
        self.request.response.setHeader("Content-type", "text/plain; charset=utf-8")
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
        split_date = view.split_date
        

        #===== header =========================================
        header = u"Paper Type; ID; "
        if ja:
            header += u"ID of corresponding DiscussionPaper;"
        if dp:
            header += u"ID of corresponding JournalArticle;"
        
        
        datestrings_1 = [
                u"Date Submission", 
                u"Date accepted as Discussion Paper", 
                u"Date published as Discussion Paper"]
        for string in datestrings_1:
            header += "%s: Year; %s: Month; %s: Day; " %(string,string,string)

        if ja:
            datestrings_2 = [
                    u"Date of paper revision", 
                    u"Date accepted as Journal Article", 
                    u"Date published as Journal Article"]
            for string in datestrings_2:
                header += "%s: Year; %s: Month; %s: Day; " %(string, string, string)
        
        header += u"Title; Authors: Surname, Firstname (Affiliation); JEL; Number of Downloads; Number of Comments; Number of Citations; Repec Handles of Citations; Policy Paper; Special Issues; Survey and Overview Paper; Number of Pages; "
        if ja:
            header += u"DOI of Journal Article; Handle/DOI of Data Set;"
        
        header += u"Download Dates;"
        
        header += "\n"
        
        #============= end header ==============================

        body = u"%s; '%s'; " %(paper.portal_type, paper.getId())
        if ja and ja_dp:
            body += u"'%s'; " %ja_dp.getId()
        if dp:
            body += u"'%s'; " %dp_ja.getId()
        
        body += u'; '.join(split_date(pdf_dates['date_submission'])) +'; '
        body += u'; '.join(split_date(pdf_dates['date_accepted_as_dp'])) +'; '

        if dp:
            body += u'; '.join(view.published_split())

        if ja:
            dp = getMultiAdapter((ja_dp, self.request), name="adata_common")
            body += u'; '.join(split_date(dp.published())) +'; '
            body += u"; ".join(split_date(pdf_dates['date_revised'])) +'; '
            body += u"; ".join(split_date(pdf_dates['date_accepted_as_ja'])) +'; '
            body += u"; ".join(view.published_split()) +'; '

        body += u"'%s'; " %paper.Title()
        
        authors = paper.getAuthorsForTitle()
        for author in authors:
            body += u"'%s, %s (%s)' " %(author.getSurname(), author.getFirstname(), author.getOrganisation())
        body += u"; "
        
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
            body += u"%s; " %i
        
        if ja:
            body += u"%s; " %view.get_doi()
            body += u"%s; " %paper_view.dataset_pi_url()
        
        ### ah, well, customer wants it, customer gets it :-)
        clickdates = view.get_clickdates()
        body += ', '.join(clickdates) + '; '
        
        

        text = header + body
        
        ### compare headline and body ###
        header_list = header.split(';')
        body_list = body.split(';')
        
        if len(header_list) == len(body_list):
            return text
        

       #i = 0
       #while header_list[i]:
       #    print "%s" %(header_list[i])
       #    i += 1
       #return printed
            
        return "Error: len_header: %s, len_body: %s" %(len(header_list), len(body_list))

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

    

