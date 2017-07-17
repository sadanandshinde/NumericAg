from ..models import PlotYield
import numpy as np
def infoRetrieval(userSite):

    print('Start, infRetrieval()')
    #find lower and upper bound of climate(AWDR) to refine search
    lound,ubound= userSite.climate.split('-')

    matchedSites=PlotYield.objects.filter(SoilType=userSite.soiltype , AWDR__gte=lound, AWDR__lte=ubound,TillType=userSite.tilltype)

    print('End, infoRetrieval(), matching sites found: count.'+ str(matchedSites.count()) )
    return matchedSites