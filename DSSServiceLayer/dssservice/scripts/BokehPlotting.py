from bokeh.plotting import figure, show
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.embed import file_html
import pandas as pd
from django.conf import settings as djangoSettings
import matplotlib.pyplot as plt
import numpy as np

def generateProfitSurfaceContourGraph(dfProfClsTrpose,userTrans):

    print('start, generateProfitSurfaceContourGraph')
    x = dfProfClsTrpose.columns.values  # np.arange(0,210,10) #np.arange(100,600,100)
    y = dfProfClsTrpose.index.values  # np.arange(100,600,100)

    X, Y = np.meshgrid(x, y)
    fig = plt.figure()
    ax = fig.add_subplot(111)

    tick = np.linspace(0, 100, 11, endpoint=True)
    #change x axis lables since inrease Nrate to 20
    xticks = np.arange(0, 210, 20)
    yticks = np.arange(0, 3100, 200)


    cset = ax.contourf(X, Y, dfProfClsTrpose.values, 60, cmap='viridis_r')
    cbar = fig.colorbar(cset, ticks=tick)

    #cbar.ax.set_ylim([0, 1])

    ax.set_xticks(xticks)
    ax.set_yticks(yticks)

    cbar.ax.set_ylabel('Achievement Probability (0% - unlikely, 100% - certainly)', fontsize=11)
    ax.set_xlabel("Nitrogen Application Rate, kg/ha", fontsize=11, fontweight='bold')
    ax.set_ylabel("NRCNF, $/ha", fontsize=11, fontweight='bold')
    ax.tick_params(axis='both', which='major', labelsize=11)

    CS2 = plt.contour(cset, levels=[50], linewidths=1,
                      colors='yellow'
                      )
    cbar.add_lines(CS2)

    # invert/reverse colorbar ticks
    cbar.ax.invert_yaxis()

    # plt.title('Porfit, Probability surface')

    # ax.clabel(cset, fontsize=9, inline=1)
    # Add label to 50% proability, findix index for 100 n rate where probability is in between 50 to 60
    IndexLvel50 = dfProfClsTrpose[(dfProfClsTrpose[100] > 50) & (dfProfClsTrpose[100] <= 60)].index[0]
    print('dfindex ', IndexLvel50)

    ax.text(100 - 10, IndexLvel50, u' 50%', color='yellow', fontsize=12)

    fig.savefig(djangoSettings.STATIC_ROOT + '/images/profitfunction/ProfitSurfacePlot_' + userTrans.user.first_name + '_' + str(
            userTrans.user.id) + '.png')
    print('Saved Contourf_ProfitSurfacePlot')

    fig.clear()

    plt.clf();
    plt.close()
    del dfProfClsTrpose

    print('End, generateProfitSurfaceContourGraph')
    return

def generateProfitfunctionImage(df,userTrans):


    ExpProfSum = list(df.loc[:, 'NRCNF'])
    Napp = list(df['N Rate'])

    EPYmax = max(ExpProfSum)  # maximum profit value
    EPNymax = Napp[ExpProfSum.index(EPYmax)]  # N rate at which maximum profit is achieved
    print('Optimum N Fertilizer rate(Nymax) '+ str(EPNymax)+' kg/ha')
    lines = plt.plot(Napp, ExpProfSum)
    # lines = plt.plot(x1, y1, x2, y2)
    # use keyword args
    plt.setp(lines, color='g', linewidth=2.0)
    # Sets x-axis
    plt.xlabel('N application, kg/ha',fontsize=11, fontweight='bold')


    # Sets y-axis
    plt.ylabel('Expected NRCNF, $/ha',fontsize=11, fontweight='bold')
    xticks = np.arange(0, 210, 20)
    yticks = np.arange(0, 3100, 200)
    plt.xticks(xticks)
    plt.yticks(yticks)


    # Adds the legend into plot
    #plt.legend((p1, p2, p3), ('line1', 'line2', 'line3'), loc='best')
    try:
        #print('STATIC ROOT ' + str( djangoSettings.STATIC_ROOT))
        plt.savefig(djangoSettings.STATIC_ROOT + '/images/profitfunction/profitfunction'+userTrans.user.first_name+'_'+str(userTrans.user.id )+'.png')
        plt.clf();
        plt.close()
        print('profit functiom image saved')
    except Exception as e:
        print('there is issue, could not generate profit function image' + str(e))

    return EPNymax


def generateProfitClassImage(df,userTrans):
    # red dashes, blue squares and green triangles
    #plt.plot(t, t, 'r--', t, t ** 2, 'bs', t, t ** 3, 'g^')
    Nrate=df['N Rate']

    line1000 = plt.plot(df['N Rate'], df.loc[:, 'prob_1000'])
    line1500 = plt.plot(df['N Rate'], df.loc[:, 'prob_1500'])
    line2000 = plt.plot(df['N Rate'], df.loc[:, 'prob_2000'])
    line2500 = plt.plot(df['N Rate'], df.loc[:, 'prob_2500'])
    lines=plt.plot( Nrate,df[ 'prob_1000'],Nrate, df[ 'prob_1500'])
    plt.setp(lines, color='g', linewidth=1.0)
    plt.plot(Nrate, df.loc[:, 'prob_2500'],'r--', Nrate, df[ 'prob_1500'],'g--')
    # use keyword args
    #plt.setp(line1000, color='g', linewidth=1.0)
    # plt.setp(line1500, color='g', linewidth=1.5)
    # plt.setp(line2000, color='g', linewidth=2.0)
    # plt.setp(line2500, color='g', linewidth=2.5)
    # Sets x-axis
    plt.xlabel('N application kg/ha')
    #plt.show()
    # Sets y-axis
    plt.ylabel('Profit $/ha')

    # Adds the legend into plot
    #plt.legend((p1, p2, p3), ('line1', 'line2', 'line3'), loc='best')
    try:
        #print('STATIC ROOT ' + str( djangoSettings.STATIC_ROOT))
        plt.savefig(djangoSettings.STATIC_ROOT + '/images/profitclasses/profitclasses'+userTrans.user.first_name+'_'+str(userTrans.user.id )+'.png')
        plt.clf();
        plt.close()
        print("profit class image saved")
    except Exception as e:
        print('there is issue, could not generate profit function image' + str(e))

    return


def plotProfitFunction(df):
    pf = figure(plot_width=650, plot_height=400, title="PASS N Application")

    pf.xaxis.axis_label = "N application rate, kg/ha"
    pf.xaxis.axis_line_width = 3
    # pf.xaxis.axis_line_color = "red"
    pf.xaxis.axis_label_text_font_size = '16pt'
    pf.xaxis.axis_label_text_font = "times"
    pf.xaxis.axis_label_text_font_style = "bold"

    # change just some things about the y-axes
    pf.yaxis.axis_label = "Profit [$\ha]"
    # pf.yaxis.major_label_text_color = "orange"
    pf.yaxis.major_label_orientation = "vertical"
    pf.yaxis.axis_label_text_font = "times"
    pf.yaxis.axis_label_text_font_style = "bold"
    pf.yaxis.axis_label_text_font_size = '16pt'

    # pf.line([Npmax, Npmax, 0], [0, pmax, pmax], line_dash=[2, 2], line_color="orange")
    ExpProfSum = list(df.loc[:, 'EProf'])
    Napp = list(df['N Rate'])
    pf.line(Napp, ExpProfSum, line_color='green', line_width=2)
    #pf.line(Napp, df.loc[:, 'NRCNF'], line_dash=[2, 2], line_color="orange", line_width=2)
    EPYmax = max(ExpProfSum)  # maximum profit value
    EPNymax = Napp[ExpProfSum.index(EPYmax)]  # N rate at which maximum profit is achieved
    pf.line([EPNymax, EPNymax, 0], [0, EPYmax, EPYmax], line_dash=[2, 2], line_color="yellow", line_width=2)
    #show(pf)# comment this, view output locally to verify

    profitHtml = file_html(pf, CDN, "Profit Function")
    return profitHtml

def plotProfitClasses(df):
    # Plotting bokeh figure
    p = figure(plot_width=650, plot_height=400, title="PASS NApplication")

    # change just some things about the x-axes
    p.xaxis.axis_label = "N application rate, kg/ha"
    p.xaxis.axis_line_width = 3
    # p.xaxis.axis_line_color = "red"

    # change just some things about the y-axes
    p.yaxis.axis_label = "Yield, t\ha"
    # p.yaxis.major_label_text_color = "orange"
    p.yaxis.major_label_orientation = "vertical"
    # p.line(xparr, yparr, line_color='green', line_width=2)

    # html = file_html(p, CDN, "my plot")


    # NreturnYmax = max(Nreturns) # maximum profit at purticular N rate
    # NreturnNmax= Napp[Nreturns.index(NreturnYmax)] # N rate where maximum profit is  achieved
    # pf.line([NreturnNmax, NreturnNmax, 0], [0, NreturnYmax, NreturnYmax], line_dash=[2, 2], line_color="green",line_width=2)
    # Probability Model
    pr = figure(plot_width=650, plot_height=400, title="PASS N Application")
    pr.xaxis.axis_label = "N application rate, kg/ha"
    pr.xaxis.axis_line_width = 3
    # pf.xaxis.axis_line_color = "red"
    pr.xaxis.axis_label_text_font_size = '16pt'
    pr.xaxis.axis_label_text_font = "times"
    pr.xaxis.axis_label_text_font_style = "bold"

    # change just some things about the y-axes
    pr.yaxis.axis_label = "Probability percentage"
    # pf.yaxis.major_label_text_color = "orange"
    pr.yaxis.major_label_orientation = "vertical"
    pr.yaxis.axis_label_text_font = "times"
    pr.yaxis.axis_label_text_font_style = "bold"
    pr.yaxis.axis_label_text_font_size = '16pt'


    pr.line(df['N Rate'], df.loc[:, 'prob_1500'], line_color='black', line_width=2, line_dash=[2, 2])
    pr.line(df['N Rate'], df.loc[:, 'prob_1000'], line_color='black', line_width=2, line_dash=[3, 3])
    pr.line(df['N Rate'], df.loc[:, 'prob_2000'], line_color='black', line_width=2, line_dash=[4, 4])
    pr.line(df['N Rate'], df.loc[:, 'prob_2500'], line_color='black', line_width=3, line_dash=[5, 5])

    show(pr)# comment this, view output locally to verify

    profitClassHtml = file_html(pr, CDN, "Profit Classes")

    return profitClassHtml