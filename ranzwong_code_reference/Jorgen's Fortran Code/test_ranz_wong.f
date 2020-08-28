c     program test_ranz_wong
c
c     Test calculations of collision efficiency.
c
c
c
c
c     Include common constants:
      include 'const_com.h'
c
      real pressure,temperature,air_density
      real true_air_speed
c
      real radius_ambient,radius_dry
c
      real mean_free_path_standard
      real pressure_standard
      real temperature_standard
c
      real mean_free_path
      real dyn_visc
c
c
c 
      real collision_efficiency
c
c
      common /ranz_wong_stuff/ mean_free_path,dyn_visc
c
c
c     Pruppacher and Klett, page 323:
      data mean_free_path_standard /6.6e-8/
      data pressure_standard /101325./
      data temperature_standard /273.16/
c
c     Dave Rogers conditions:
c     data pressure /100000./
      data pressure /100056./
      data temperature /288.37/
c     data true_air_speed /100./
c     data true_air_speed /12./
      data true_air_speed /8./
c     data true_air_speed /4./
      data radius_ambient /5.085e-6/
      data radius_dry /3.838e-6/
c
c     rel_hum_exposure_bar for sli_081018a3:
c     70.42%
c     altitude:
c     141 m.
c
c
c     radius_ambient=radius_ambient/3.838*2.
c     radius_ambient=radius_ambient/3.838*2.*1.5
      radius_ambient=radius_ambient/3.838*2.*1.5*1.333333333
c     radius_dry=radius_dry/3.838*2.
c     radius_dry=radius_dry/3.838*2.*1.5
      radius_dry=radius_dry/3.838*2.*1.5*1.333333333
c     radius_ambient=radius_ambient/3.28
c     radius_dry=radius_dry/3.28
c
c
      call const
c
c
c     Mean free path of air molecules:
      mean_free_path=mean_free_path_standard*
     c (pressure_standard/pressure)*
     c (temperature/temperature_standard)
c
c
c     Dynamic viscosity:
c     if(temperature.ge.t_offset) then
c       CHECK:
c       dyn_visc=(1.718+0.0049*(temperature-t_offset))*1.e-4
c     else
c       CHECK:
c       dyn_visc=(1.718+0.0049*(temperature-t_offset)-
c    c   1.2e-5*(temperature-t_offset)**2.)*1.e-4
c     endif
      call get_dyn_visc(temperature,dyn_visc)
c
c
c
c     Find collision efficiency between ambient
c     particle and glass slide "ribbon":
      air_density=pressure/(rd*temperature)
      call ranz_wong(pressure,temperature,air_density,
     c true_air_speed,
     c radius_dry,radius_ambient,
     c collision_efficiency)
c
c
      write(*,*) 'test_ranz_wong: collision_efficiency=',
     c collision_efficiency
c
c
      stop
      end
