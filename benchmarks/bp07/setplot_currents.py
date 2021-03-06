
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 

import numpy as np
import matplotlib.pyplot as plt

#--------------------------
def setplot(plotdata):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of pyclaw.plotters.data.ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 


    from pyclaw.plotters import colormaps, geoplot

    plotdata.clearfigures()  # clear any old figures,axes,items data

    def set_drytol(current_data):
        # The drytol parameter is used in masking land and water and
        # affects what color map is used for cells with small water depth h.
        # The cell will be plotted as dry if h < drytol.
        # The best value to use often depends on the application and can
        # be set here (measured in meters):
        current_data.user.drytol = 1.e-4


    plotdata.beforeframe = set_drytol

    # To plot gauge locations on pcolor or contour plot, use this as
    # an afteraxis function:

    def addgauges(current_data):
        from pyclaw.plotters import gaugetools
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos='all', format_string='ko', add_labels=True)
             
             

    # ========================================================================
    #  Water Velocity Helper Functions
    # ========================================================================        
    def water_velocity(current_data,DRY_TOL=1e-6):
        r"""Calculate velocity from the momentum and depth
        
        Calculates the x and y velocities from the momenta.  A mask is 
        constructed so that division by a small depth is avoided, controlled
        by the optional keyword argument DRY_TOL (default = 1e-6).  A check
        for NaNs is also made.  Any point not satisfying either of these
        criteria is set to 0.0.
        
        returns numpy.ndarray, nump.ndarray
        """
        h = current_data.q[:,:,0]
        hu = current_data.q[:,:,1]
        hv = current_data.q[:,:,2]
        u = np.zeros(hu.shape)
        v = np.zeros(hv.shape)
        
        index = np.nonzero((np.abs(h) > DRY_TOL) * (h != np.nan))
        u[index[0],index[1]] = hu[index[0],index[1]] / h[index[0],index[1]]
        v[index[0],index[1]] = hv[index[0],index[1]] / h[index[0],index[1]]
        
        return u,v
        
    def vorticity(current_data):
        r"""Calculate vorticity of velocity field
        
        Using matrix operations, calculate u_y + v_x, note that second order,
        centered differences are used for interior points and forward and
        backward differences for the boundary values.
        
        returns numpy.ndarray of shape of u and v
        """
        u,v = water_velocity(current_data)
        dx = current_data.dx
        dy = current_data.dy
        
        u_y = np.zeros(u.shape)
        u_y[:,0] = (-3.0*u[:,0] + 4.0 * u[:,1] - u[:,2]) / (2.0 * dy)
        u_y[:,-1] = (u[:,-3] - 4.0 * u[:,-2] + 3.0 * u[:,-1]) / (2.0 * dy)
        u_y[:,1:-1] = (u[:,2:] - u[:,0:-2]) / (2.0 * dy)

        v_x = np.zeros(v.shape)
        v_x[0,:] = (-3.0*v[0,:] + 4.0 * v[1,:] - v[2,:]) / (2.0 * dx)
        v_x[-1,:] = (u[-3,:] - 4.0 * u[-2,:] + 3.0 * u[-1,:]) / (2.0 * dx)
        v_x[1:-1,:] = (v[2:,:] - v[0:-2,:]) / (2.0 * dx)
        
        return v_x - u_y
        
        
    def water_speed(current_data):
        u,v = water_velocity(current_data)
        return np.sqrt(u**2+v**2)
        
    def water_quiver(current_data):
        u = water_u(current_data)
        v = water_v(current_data)
            
        plt.hold(True)
        Q = plt.quiver(current_data.x[::2,::2],current_data.y[::2,::2],
                        u[::2,::2],v[::2,::2])
        max_speed = np.max(np.sqrt(u**2+v**2))
        label = r"%s m/s" % str(np.ceil(0.5*max_speed))
        plt.quiverkey(Q,0.15,0.95,0.5*max_speed,label,labelpos='W')
        plt.hold(False)    
    

    #-----------------------------------------
    # Figure for pcolor plot
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='pcolor', figno=0)
    plotfigure.show = False

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = True

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -0.02
    plotitem.pcolor_cmax = 0.02
    plotitem.add_colorbar = True
    plotitem.amr_gridlines_show = [0,0,0]
    plotitem.amr_gridedges_show = [1]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = geoplot.land
    plotitem.pcolor_cmap = geoplot.land_colors
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 0.05
    plotitem.add_colorbar = False
    plotitem.amr_gridlines_show = [0,0,0]
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'

    

    #-----------------------------------------
    # Figure for imshow plot
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Surface and Gauge 1', figno=20)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('imshow')
    plotaxes.axescmd = "axes([.1,.5,.8,.4])"
    plotaxes.title = 'Surface'
    plotaxes.scaled = True
    plotaxes.afteraxes = addgauges

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.imshow_cmap = geoplot.tsunami_colormap
    plotitem.imshow_cmin = -0.03
    plotitem.imshow_cmax = 0.03
    plotitem.add_colorbar = True
    plotitem.amr_gridlines_show = [0,0,0]
    plotitem.amr_gridedges_show = [1]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = geoplot.land
    plotitem.imshow_cmap = geoplot.land_colors
    plotitem.imshow_cmin = 0.0
    plotitem.imshow_cmax = 0.05
    plotitem.add_colorbar = False
    plotitem.amr_gridlines_show = [0,0,0]
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'


    # Gauge trace:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.axescmd = "axes([.1,.1,.8,.3])"
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = [-0.02, 0.05]
    plotaxes.title = 'Gauge 1'

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_gauge_trace')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'
    plotitem.gaugeno = 1


    #-----------------------------------------
    # Figure for zoom
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Zoom', figno=10)
    #plotfigure.show = False
    plotfigure.kwargs = {'figsize':[12,7]}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('monai')
    #plotaxes.axescmd = 'axes([0.0,0.1,0.6,0.6])'
    plotaxes.title = 'Zoom near Monai Valley'
    plotaxes.scaled = True
    plotaxes.xlimits = [4.0, 5.2]
    plotaxes.ylimits = [1.3, 2.5]

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -0.02
    plotitem.pcolor_cmax = 0.02
    plotitem.add_colorbar = True
    plotitem.amr_gridlines_show = [0]
    plotitem.amr_gridedges_show = [1]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = geoplot.land
    plotitem.pcolor_cmap = geoplot.land_colors
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 0.05
    plotitem.add_colorbar = False
    plotitem.amr_gridlines_show = [0]

    # Add contour lines of bathymetry:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = geoplot.topo
    from numpy import arange, linspace
    plotitem.contour_levels = arange(-0.02, 0., .0025)
    plotitem.amr_contour_colors = ['k']  # color on each level
    plotitem.kwargs = {'linestyles':'solid'}
    plotitem.amr_contour_show = [1]  # show contours only on finest level
    plotitem.gridlines_show = 0
    plotitem.gridedges_show = 0
    plotitem.show = True
    
    # Add contour lines of topography:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = geoplot.topo
    from numpy import arange, linspace
    plotitem.contour_levels = arange(0., .2, .01)
    plotitem.amr_contour_colors = ['w']  # color on each level
    plotitem.kwargs = {'linestyles':'solid'}
    plotitem.amr_contour_show = [1]  # show contours only on finest level
    plotitem.gridlines_show = 0
    plotitem.gridedges_show = 0
    plotitem.show = True

    # Add dashed contour line for shoreline
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = geoplot.topo
    plotitem.contour_levels = [0.]
    plotitem.amr_contour_colors = ['k']  # color on each level
    plotitem.kwargs = {'linestyles':'dashed'}
    plotitem.amr_contour_show = [1]  # show contours only on finest level
    plotitem.gridlines_show = 0
    plotitem.gridedges_show = 0
    plotitem.show = True




    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Surface & topo', figno=300, \
                    type='each_gauge')

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = [0,60]
    plotaxes.ylimits = [-0.02, 0.05]
    plotaxes.title = 'Surface'

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'

    # Plot topo as green curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')

    def gaugetopo(current_data):
        q = current_data.q
        h = q[:,0]
        eta = q[:,3]
        topo = eta - h
        return topo
        
    plotitem.plot_var = gaugetopo
    plotitem.clf_each_gauge = False
    plotitem.plotstyle = 'g-'
    def afteraxes(current_data):
        from pylab import plot, legend, loadtxt
        t = current_data.t
        plot(t, 0*t, 'k')
        try:
            labgage = loadtxt('WaveGages.txt',skiprows=1)
        except:
            print "*** Did not find WaveGages.txt from benchmark"
        gaugeno = current_data.gaugeno
        
        if gaugeno in [1,2,3]:
            plot(labgage[:,0],0.01*labgage[:,gaugeno],'r')
            legend(('GeoClaw','topography','sea level','lab data'),loc='upper right')
        else:
            legend(('GeoClaw','topography','sea level'),loc='upper right')
            
        

    plotaxes.afteraxes = afteraxes


    #-----------------------------------------
    # Figure for grids alone
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='grids', figno=2)
    plotfigure.show = False

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = [0,1]
    plotaxes.ylimits = [0,1]
    plotaxes.title = 'grids'
    plotaxes.scaled = True

    # Set up for item on these axes:
    plotitem = plotaxes.new_plotitem(plot_type='2d_grid')
    plotitem.amr_grid_bgcolor = ['#ffeeee', '#eeeeff', '#eeffee']
    plotitem.amr_gridlines_show = [1,1,0]   
    plotitem.amr_gridedges_show = [1]     
    
    
    # ========================================================================
    #  Water Currents
    # ========================================================================
    max_speed = 1.0
    
    # ========================================================================
    # Full plot
    plotfigure = plotdata.new_plotfigure(name='currents', figno=400)
    plotfigure.kwargs = {'figsize':[12,7]}
    plotfigure.show = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Currents Full Domain'
    plotaxes.scaled = True

    # Speed
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = water_speed
    plotitem.imshow_cmap = plt.get_cmap('PuBu')
    plotitem.imshow_cmin = 0.0
    plotitem.imshow_cmax = max_speed
    plotitem.add_colorbar = True
    plotitem.amr_gridlines_show = [0,0,0]
    plotitem.amr_gridedges_show = [1]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = geoplot.land
    plotitem.imshow_cmap = geoplot.land_colors
    plotitem.add_colorbar = False
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 0.05
    
    # ========================================================================
    # Zoomed plot
    plotfigure = plotdata.new_plotfigure(name='currents_zoomed', figno=401)
    plotfigure.kwargs = {'figsize':[12,7]}
    plotfigure.show = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Currents Zoomed Domain'
    plotaxes.scaled = True
    plotaxes.xlimits = [4.0, 5.2]
    plotaxes.ylimits = [1.3, 2.5]

    # Speed
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = water_speed
    plotitem.imshow_cmap = plt.get_cmap('PuBu')
    plotitem.imshow_cmin = 0.0
    plotitem.imshow_cmax = max_speed
    plotitem.add_colorbar = True
    plotitem.amr_gridlines_show = [0,0,0]
    plotitem.amr_gridedges_show = [1]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = geoplot.land
    plotitem.imshow_cmap = geoplot.land_colors
    plotitem.add_colorbar = False
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 0.05
    
    # ========================================================================
    # Vorticity plot
    vorticity_limits = [-3,3]
    #  Full domain
    plotfigure = plotdata.new_plotfigure(name='full_vorticity', figno=500)
    plotfigure.show = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Vorticity'
    plotaxes.scaled = True

    # Speed
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = vorticity
    plotitem.imshow_cmap = colormaps.make_colormap({1.0:'r',0.5:'w',0.0:'b'})
    plotitem.imshow_cmin = vorticity_limits[0]
    plotitem.imshow_cmax = vorticity_limits[1]
    plotitem.add_colorbar = True
    plotitem.amr_gridlines_show = [0,0,0]
    plotitem.amr_gridedges_show = [1]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = geoplot.land
    plotitem.imshow_cmap = geoplot.land_colors
    plotitem.add_colorbar = False
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 0.05

    #-----------------------------------------
    
    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_gaugenos = [1,2,3,12]  # list of gauges to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?

    return plotdata

    
