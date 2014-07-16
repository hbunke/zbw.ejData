from Products.Five.browser import BrowserView
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from collections import OrderedDict
from Products.CMFCore.utils import getToolByName


try:
    import json
except ImportError:
    # Python 2.5/Plone 3.3 use simplejson
    import simplejson as json


class View(BrowserView):
    """
    json view for article level metrics and data
    """
    
    #template = ViewPageTemplateFile("json.pt")


    def __call__(self):
        self.request.set('disable_border', True)
        #return self.template
        self.request.response.setHeader("Content-type", "application/json; charset=utf-8")
        self.request.response.setHeader("Content-Transfer-Encoding", "8bit")
        #return self.template()
        return self.json()


    def json(self):
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
        
        
        #using OrderedDict since we want to preserve the order of attributes
        jo = OrderedDict()
        
        jo['portal_type'] = paper.portal_type
        jo['id'] = paper.id

        #corresponding paper TODO: URL and other metadata
        corr_paper = {}
        if ja and ja_dp:
            p = ja_dp
        if dp and dp_ja:
            p = dp_ja
        try:
            corr_paper['type'] = p.portal_type
            corr_paper['id'] = p.getId()
            corr_paper['url'] = p.absolute_url()
        except:
            pass
        jo['corresponding_paper'] = corr_paper
        
        jo['date_of_submission'] = pdf_dates['date_submission']
        jo['date_accepted_as_DP'] = pdf_dates['date_accepted_as_dp']
        
        if dp:
            jo['date_published_as_DP'] = view.published()
        if ja:
            corr_dp = getMultiAdapter((ja_dp, self.request), name="adata_common")
            jo['date_published_as_DP'] = corr_dp.published()
            jo['date_revised'] = pdf_dates['date_revised']
            jo['date_accepted_as_JA'] = pdf_dates['date_accepted_as_ja']
            jo['date_published_as_JA'] = view.published()
        
        jo['title'] = paper.Title()

        #authors
        authors = paper.getAuthorsForTitle()
        jo['authors'] = authorlist = []
        for author in authors:
            a = OrderedDict()
            a['id'] = author.getId()
            a['name'] = author.getFullname()
            a['affiliation'] = author.getOrganisation()
            if author.getHomepage() == "http://":
                a['url'] = ''
            else:
                a['url'] = author.getHomepage()
            a['economics_url'] = author.absolute_url()
            
            a['other_papers_in_economics'] = paper_list = []
            opapers = self.author_papers(author.getId())
            for opaper in opapers:
                if opaper.getId() != paper.getId():
                    p = OrderedDict()
                    p['type'] = opaper.portal_type
                    p['id'] = opaper.getId()
                    p['url'] = opaper.absolute_url()
                    paper_list.append(p)
                else:
                    pass
            authorlist.append(a)

            jo['JEL'] = paper.getJel()
            jo['downloads'] = view.downloads()
            jo['download_dates'] = self.get_clickdates()
            
            
            #comments
            commentsdb = self.get_comments()
            jo['number_of_comments'] = len(commentsdb)
            comments = []
            for comment in commentsdb:
                comment_view = getMultiAdapter((comment, self.request), name='commentView')
                date = comment_view.getDate()
                
                #XXX change this to method in commentsView which doesn't
                #display anonymous authors
                author = self.comment_author(comment)
                
                #url = comment.absolute_url()
                url = comment_view.getCommentURL()
                c = OrderedDict()
                c['date'] = date
                c['author'] = author
                c['url'] = url
                comments.append(c)
                
            jo['comments'] = comments
            
            jo['number_of_citations'] = citation_view.count()
            jo['citation_handles'] = view.citation_handles(output='json')
            jo['Policy_Paper'] = paper.isPolicyPaper
            jo['Survey_And_Overview_Paper'] = paper.isSurveyAndOverviewPaper
            jo['Special_Issue'] = paper.getSpecialIssues()
            jo['pages'] = paper.getPages()


        pretty = json.dumps(jo, sort_keys=False, indent=4)

        return pretty

        
    
    def author_papers(self, author):
        """
        return all papers of author
        """
        
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type=('DiscussionPaper', 'JournalPaper'),
                ej_authors_id=author)
        return [brain.getObject() for brain in brains]


    def comment_author(self, comment):

        if comment.getName() != "":
            return comment.getName()
                    
        referee = comment.getReferee()
        if len(referee) > 0:
            return referee
                        
        mtool = getToolByName(comment, "portal_membership")        
        creator = comment.Creator()
        mi = mtool.getMemberInfo(creator);
        if mi and mi['fullname']:
            return mi['fullname']

        return comment.Creator()

    
    def get_comments(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(
            path="/".join(self.context.getPhysicalPath()),
            portal_type="Comment"
        )
        return [brain.getObject() for brain in brains]

        
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
