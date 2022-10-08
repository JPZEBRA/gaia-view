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
    pyplot.xlim(0,30000)
    pyplot.ylim(-150,150)

    global fig_closed
    fig_closed = False
    fig.canvas.mpl_connect('close_event', handle_close)

    ax = fig.gca()
    ax.set_facecolor("white")

    ax.axes.xaxis.set_visible(True)
    ax.axes.yaxis.set_visible(True)

    cr = []
    cd = []
    pr = []
    pd = []
    sz = []

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

                cr.append(r[i]['ra'])
                cd.append(r[i]['dec'])
                pr.append(r[i]['pmra'])
                pd.append(r[i]['pmdec'])
                sz.append(abs(r[i]['parallax']))

    tc = 0

    print(f">>> DRAWING <<<")

    for z in range (0,len(cd)) :

        dd = cd[z]
        ar = pr[z]
        ad = pd[z]
        ss = sz[z]

        if not (abs(ar) >= 0 and abs(ad) >= 0 ) :
            continue
        if not ss>0 :
            continue

        dist = 1/math.tan(ss/2000/60/60*math.pi/180)
        dly = dist/63241.077084
        cv = 149597870.7/365.2422/24/60/60
        vr = dist*math.tan(ar/1000/60/60*math.pi/180)*math.cos(dd*math.pi/180)*cv
        vd = dist*math.tan(ad/1000/60/60*math.pi/180)*cv

        pyplot.plot(dly,vr,marker=".",color="green",markersize=1)
        pyplot.plot(dly,vd,marker=".",color="blue",markersize=1)

    pyplot.text(28000,170,"horizontal (km/s)",fontsize=14,color="green")
    pyplot.text(28000,150,"vertical (km/s)",fontsize=14,color="blue")
    pyplot.text(28000,0,"dist (l.year)",fontsize=14,color="black")

    pyplot.text(0,170,"RA:" + str(rah) + " DEC:" + str(dcd) ,fontsize=14,color="lightgreen")
    pyplot.text(0,-170,"This work has made use of data from the European Space Agency (ESA) mission Gaia" ,fontsize=14,color="orange")
    pyplot.text(0,-190," (https://www.cosmos.esa.int/gaia)" ,fontsize=14,color="orange")

    pyplot.savefig("velo.png")

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

window = sg.Window('GAIA VELOCITY VIEWER Ver0.1rev',layout)

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



