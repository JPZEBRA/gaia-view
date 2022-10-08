#
# DATA PLOTTER OF SATELLITE GAIA VERSION 0.1.0 rev1
#      WIDE MOSAIC QUERY VERSION
# SCRIPTED BY JPZEBRA@GITHUB 2022.10.07
#

# GUI MENU
import PySimpleGUI as sg

# PLOT
import math
from matplotlib import pyplot

# GAIA DB ACCESS
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
Gaia.MAIN_GAIA_TABLE = "gaiaedr3.gaia_source" # Select early Data Release 3
Gaia.ROW_LIMIT = -1

# SETTINGS

rah =  12.0
dcd =   0.0

cx = 0
cy = 0

ex = 1.0

wd = 2.0
ht = 1.0

fx = 100.0

sz = 3






# SUB ROUTINES

def check_and_set_values() :

    global rah
    global dcd

    global ex
    global fx

    global cx
    global cy
    global wd
    global ht

    if rah <   0 : rah =   0
    if rah >  24 : rah =  24
    if dcd < -90 : dcd = -90
    if dcd > +90 : dcd = +90

    cx = rah*360/24
    cy = dcd

    if ex < 0.1 : ex = 0.1
    if fx < 1.0 : fx = 1.0

    wd = math.ceil(2.0/ex*4)
    ht = math.ceil(1.0/ex*4)

def star_bright(b,f) :

    P = 0

    if -10 < b and b < 30 :
        P = math.exp( ( 2.5 - b ) / 2.5 ) * f

    return P

def star_color(r,g,b,f) :
    rr = star_bright(r,f)
    gg = star_bright(g,f)
    bb = star_bright(b,f)
    mx = rr
    if gg > mx : mx = gg
    if bb > mx : mx = bb
    if mx<=0 : return (0,0,0)
    return (rr/mx,gg/mx,bb/mx)

def star_ave(r,g,b) :
    sum = 0
    cnt = 0
    if -10<r and r<30 :
        sum = sum + r
        cnt = cnt + 1 
    if -10<g and g<30 :
        sum = sum + g
        cnt = cnt + 1 
    if -10<b and b<30 :
        sum = sum + b
        cnt = cnt + 1
    if cnt>0 : return sum/cnt
    return 30.0 

def star_size(av,f) :
    global sz
    return star_bright(av,f)*sz

fig_closed = True

def handle_close(evt) :
    global fig_closed
    fig_closed = True
    print("figure closed.")






# MAIN ROUTINE

def draw_star(refresh) :

    check_and_set_values()

    global cx
    global cy
    global wd
    global ht

    global ex
    global fx

    fig = pyplot.figure("GAIA VIEW")
    fig.set_size_inches(14,7)
    pyplot.xlim(-100,100)
    pyplot.ylim(-50,50)

    global fig_closed
    fig_closed = False
    fig.canvas.mpl_connect('close_event', handle_close)

    ax = fig.gca()
    ax.set_facecolor("black")

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    xx = []
    yy = []
    tg = []
    cl = []
    ss = []

    for vy in range(0,ht) :
        dy = (vy/2-ht/4+0.25)
        for vx in range(0,wd) :
            dx = (vx/2-wd/4+0.25)
            coord  = SkyCoord(ra=cx+dx, dec=cy+dy, unit=(u.degree, u.degree), frame='icrs')
            width  = u.Quantity(0.5, u.deg)
            height = u.Quantity(0.5, u.deg)

            print(f">>> DATA ({vy},{vx}) <<<")

            r = Gaia.query_object_async(coordinate=coord, width=width, height=height)

            if len(r)<1 : continue

            for i in range(0,len(r)-1) :
                print(" id " + str(r[i]['source_id']) + " parallax " + str(r[i]['parallax']))
                print(" ra " + str(r[i]['ra']) + " dec " + str(r[i]['dec']) + " pmra " + str(r[i]['pmra']) + " pmdec " + str(r[i]['pmdec']))
                print(" GBR " + str(r[i]['phot_g_mean_mag']) + " " + str(r[i]['phot_bp_mean_mag']) + " " + str(r[i]['phot_rp_mean_mag']))

                tg.append(r[i]['source_id'])
                xx.append((cx -r[i]['ra'])*50*ex)
                yy.append((r[i]['dec'] - cy)*50*ex)
                rr = r[i]['phot_rp_mean_mag']
                gg = r[i]['phot_g_mean_mag']
                bb = r[i]['phot_bp_mean_mag']
                av = star_ave(rr,gg,bb)
                cl.append(star_color(rr,gg,bb,fx))
                ss.append(star_size(av,fx))

    tc = 0

    for zz in range(0,8) :

        print(f">>> DRAWING {zz} <<<")

        rmax = math.pow(2,6-zz)
        rmin = rmax/2

        if zz==0 : rmax = 100
        if zz==7 : rmin = 0

        for z in range (0,len(tg)) :
            if rmin <= ss[z] and ss[z]<= rmax :
                if ss[z]>3 : pyplot.plot(xx[z],yy[z],marker=".",color="black",markersize=ss[z]+1)
                pyplot.plot(xx[z],yy[z],marker=".",color=cl[z],markersize=ss[z])
                if tc<128 :
                    pyplot.text(xx[z],yy[z],tg[z],fontsize=8,color="cyan")
                    tc = tc + 1

    pyplot.text(-100,46,"RA:" + str(rah) + " DEC:" + str(dcd) ,fontsize=14,color="lightgreen")
    pyplot.text(-100,-46,"This work has made use of data from the European Space Agency (ESA) mission Gaia" ,fontsize=14,color="orange")
    pyplot.text(-100,-49," (https://www.cosmos.esa.int/gaia)" ,fontsize=14,color="orange")

    pyplot.savefig("gaia.png")

    pyplot.show()






# GUI MENU

sg.theme('BlueMono')

layout = [ [sg.Text('VIEWER OF SATELLITE GAIA DATA')],
           [sg.Text(' RA (h) '),sg.InputText('0.000000',size=(12,1),key='rah'),
            sg.Text(' DEC(d) '),sg.InputText('0.000000',size=(12,1),key='dec')],
           [sg.Text(' EXPAND '),sg.InputText('1.0000',size=(8,1),key='ext'),
            sg.Text(' BRIGHT '),sg.InputText('100.00',size=(8,1),key='brt')],
           [sg.Button('OK'),sg.Button('CANCEL')]
         ]

closed = False

window = sg.Window('GAIA STAR VIEWER Ver0.1rev',layout)

while not closed :

    event, values = window.read()

    if event == sg.WIN_CLOSED : closed = True

    elif event == 'CANCEL' : closed = True

    elif event == 'OK' and fig_closed:

        try :
            rah = float(values['rah'])
            dcd = float(values['dec'])
            ex  = float(values['ext'])
            fx  = float(values['brt'])
            draw_star(True)
        except ValueError :
            print("Value Erroor !")


# FILE END



