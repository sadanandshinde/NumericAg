from django.shortcuts import render
from .models  import UserRquestSite,UserTransaction

import schedule
import time, threading
from django.http import HttpResponse,HttpResponseRedirect
from queue import Queue
import numpy as np
import pandas as pd
#from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings as djangoSettings
from .scripts import sensitivitysimulation,BeansNDistributionCreator, BokehPlotting, Utility, SimilarityFinder
from datetime import datetime
import itertools
import logging, gc
from django_pandas.io import read_frame
#import multiprocessing
# Create your views here.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - (%(threadName)-10s)- %(levelname)s - %(message)s')

'''
Numeric Simulation logic for 5 independent variables(Price , cost, Y0, Ymax,Nymax etc)
assumed everything normal distribution for now, read ECPA 2017 paper
'''

def callSimulation(rs):
    logger.info('start, callSimulation()')
    logger.debug (threading.currentThread().getName()+ '  Starting')

    #find user site details by trasnsaction id


    '''
    Simulation Analysis start
    '''
    startTime = datetime.now()

    print('userSiteReq: ' + str(rs.id))
    logger.debug('user site parameters')
    logger.debug(rs.usersite.id)


    # fetch matching records from database
    # logger.debug("calling filter for matching records")
    # resultset = PDataset1.objects.filter(AWDR__gte=lbound, AWDR__lte=ubound, SoilType=soiltype, TillType=tilType)
    logger.info("calling inforRetrieval()")
    dataset = SimilarityFinder.infoRetrieval(rs.usersite)
    if dataset.count() <1:
        #status 0: pending, 1:completed, 2: unproccessed
        Utility.updateTransParams(rs, status=2, emailFlag='N',processTime=None)
        Utility.emailNoMatchingSiteFoundtoUser(rs.user)
        return

    # converting the queryset into pandas dataframe
    #dfResult = read_frame(resultset)
    dfDataset = read_frame(dataset) #pd.DataFrame.from_records(dataset.values_list())
    #print('dfDataset', dfDataset.head(5))
    #print('dfDataset as matrix', dfDataset.as_matrix())
    #print('dfDataset as values ', dfDataset.values)

    MeanPrice = rs.usersite.price_mean  #175
    StdPrice = rs.usersite.price_std #20
    # trying new approach for Price and Cost Prob from PDF function
    normPrice = np.linspace(130, 220,7)  # BinsNDistributionCreator.normIntervals(MeanPrice, StdPrice, 7)  # [130,145,160,175,190,205,220]#
    print("=====price===== " + str(normPrice))
    cY = normPrice.tolist()
    vectorcY = BeansNDistributionCreator.findProbabilityNDensity(normPrice, MeanPrice, StdPrice)

    MeanCost =  rs.usersite.costmean #1
    StdCost =  rs.usersite.coststd #0.25
    cost = np.linspace(0.4, 1.6, 7)  # BinsNDistributionCreator.normIntervals(MeanCost, StdCost, 7)
    print("=====normCost===== " + str(cost))
    cN = cost.tolist()
    vectorcN = BeansNDistributionCreator.findProbabilityNDensity(cost, MeanCost, StdCost)

    dltYld = 0.5

    Ymin = np.arange(0, 20 + dltYld, dltYld)
    Ymax = np.arange(0, 20 + dltYld, dltYld)
    Nymax = np.arange(10, 260, 10)

    # saving the production and profit input parameters to dataframe, local csv file
    dfInput = pd.DataFrame(index=np.arange(0, len(Ymax)))
    dfInput['Y0'] = pd.Series(Ymin, index=np.arange(0, len(Ymin)))
    dfInput['Ymax'] = pd.Series(Ymax, index=np.arange(0, len(Ymax)))
    dfInput['Nymax'] = pd.Series(Nymax, index=np.arange(0, len(Nymax)))
    dfInput['cY'] = pd.Series(cY, index=np.arange(0, len(cY)))
    dfInput['cN'] = pd.Series(cN, index=np.arange(0, len(cN)))
    dfInput.index.name = 'index'
    print(dfInput.head())

    #dfInput.to_csv('C:/Users/Student.Student11.000/Desktop/AgriDSS/Data/Sadanand/dfInputs' + soilTexture + '.csv')
    dfInput.to_csv(djangoSettings.STATIC_ROOT + '/datafiles/UserSiteParams_'+rs.user.first_name+'_'+str(rs.user.id )+'.csv', encoding='utf-8')

    # define the production paramters for combinations
    iterables = [Ymin, Ymax, Nymax]

    # products of the production paramters , numpy array
    products = [np.array(p) for p in itertools.product(*iterables)]
    print('all combinations count ' + str(len(products)))

    # create dataframe of the production paramters with respective columns
    dfAllProducts = pd.DataFrame(products, columns=['Y0', 'Ymax', 'Nymax'])
    # print(dfAllProducts.head())
    print("dfAllProducts count" + str(dfAllProducts.count()))

    # delete rows where Y0>Ymax from the dataframe
    dfProducts = dfAllProducts.drop(dfAllProducts[dfAllProducts.Y0 > dfAllProducts.Ymax].index)
    print("Combinations count after ymin check " + str(dfProducts.count(axis=0)))

    # aggregate all input variables in a dataframe
    # dfInputs = pd.DataFrame({'cY': cY, 'cN': cN, 'Ymin': Ymin, 'Ymax': Ymax, 'NYmax': Nymax})
    # print(dfInputs.head())
    # dfInputs.to_csv('C:/Users/Student.Student11.000/Desktop/AgriDSS/Data/dfInputs.csv')

    print('===Calling errorToProbabilityCalculation () =====')
    dfProducts = sensitivitysimulation.errorToProbabilityCalculation(dfProducts, dataset)
    #dfProducts.to_csv('C:/Users/Student.Student11.000/Desktop/AgriDSS/Data/Sadanand/dfProducts'+soilTexture+'.csv')
    dfProducts.to_csv(djangoSettings.STATIC_ROOT + '/datafiles/ProductionParamsProb'+rs.user.first_name+'_'+str(rs.user.id )+'.csv', encoding='utf-8')
    print('===Calling profitSensitivityAnalysis()===')
    # calling to script module for numeric simulation or sensitivity analysis
    df = sensitivitysimulation.profitSensitivityAnalysis(dfProducts, vectorcY, vectorcN, rs)

    print(df.head())

    print("Total End Time Diffrenence")
    print(datetime.now() - startTime)

    print('plotting matplotlib Grpahs ')
    #pfModel = BokehPlotting.plotProfitFunction(df)
    optNrate=BokehPlotting.generateProfitfunctionImage(df,rs)
    # call to proft classes functuion
    #profClasses = BokehPlotting.plotProfitClasses(df)
    #BokehPlotting.generateProfitClassImage(df,rs)

    #additng percentage to show as suffix to the probability columns
    df['NRCNF > 1000'] =   df['NRCNF > 1000'].astype(str) +' %'
    df['NRCNF > 1500'] = df['NRCNF > 1500'].astype(str) + ' %'
    df['NRCNF > 2000'] = df['NRCNF > 2000'].astype(str) + ' %'
    df['NRCNF > 2500'] = df['NRCNF > 2500'].astype(str) + ' %'

    #rename columns specific to user understanding view show
    df.rename(columns={'N Rate':'N rate kg/ha','NRCNF': 'Expected NRCF $/ha', 'EFB': 'EFB $/ha','NRCNF > 1000':'NRCF > 1000 $/ha',
                       'NRCNF > 1500':'NRCF > 1500 $/ha','NRCNF > 200':'NRCF > 2000 $/ha','NRCNF > 2500':'NRCF > 2500 $/ha'}, inplace=True)

    # converting the dataframe results to html table format to show on result page
    dfProfCls = df.to_html(index=False)

    del df
    gc.collect()

    print('Emailing the Results to user  ')
    context = {  'dfresult': dfProfCls,'optNrate':optNrate,'user':rs.user,'siteInfo':rs.usersite}
    #return render(request, 'passapp/result.html', context)
    #Send Email module here
    if Utility.EmailResultsToUser(context,rs.user):

        logger.info('Email sent successfully')

        Utility.updateTransParams(rs,status=1,emailFlag='Y',processTime=datetime.now()- startTime)

        logger.info('trans flags(status, email) has been  updated/saved  ')

    logger.info('end, callSimulation()')
    return


def job():
    logger.info(" Job started, I'm working...")
    #print('active thread list : '+ str(threading.enumerate()))
    actThreadCount=threading.activeCount()
    logger.info( 'active thread counts:  ' + str(actThreadCount))

    logger.debug('fetching pending  user transaction request from database ')
    pendingrequests = UserTransaction.objects.filter(status=0)
    logger.debug('pendingrequests counts : '+ str(pendingrequests.count()))

    if not pendingrequests.count()>=1:
        logger.debug('No pending request found ')
        return
        #raise Exception("Couldn't find IMGUR_CLIENT_ID environment variable!")

    logger.info('iterating pendingrequests')

    for rs in pendingrequests:
        try:

            if actThreadCount <=10 and not threading.currentThread().getName() == rs.id:
                    logger.debug('started user trans id ' + str(rs.id))
                    logging.debug('calling startSimulation')

                    t = threading.Thread(name=rs.id, target=callSimulation(rs))
                    logger.info(str(threading.currentThread().getName()) +' Starting')
                    time.sleep(4)
                    logger.debug('Thread started for site request ' + str(rs.usersite_id))
                    t.start()

                    logger.info('Thread processing finished for user transaction: '+str(rs.id))

                    #send email here
        except Exception as e:
            logger.error('Exception in thread execution '+e)



def startJob(request):


    logger.info('startJob(), calling job scheduler')


    schedule.every(20).seconds.do(job)
    # schedule.every().hour.do(job)
    # schedule.every().day.at("10:30").do(job)

    while 1:
        schedule.run_pending()
        time.sleep(4)
    return  HttpResponse('Job Schedular started :')
