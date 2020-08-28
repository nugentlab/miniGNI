      subroutine ranz_wong(pressure,temperature,air_density,
     c true_air_speed,
     c radius_dry,radius_ambient,
     c collision_efficiency)
c
c     Calculate the collision efficiency between a sphere and a ribbon
c     following Ranz and Wong (1952): The impaction of dust and smoke
c     particles on surface and body collectors. Industrial and
c     Engineering Chemistry, vol 44, p 1372-1381.
c
      include 'const_com.h'
c
      real pressure
      real temperature
      real air_density
      real true_air_speed
      real radius_dry,radius_ambient
      real particle_density
c
      real density_salt
      real volume_salt,volume_water,volume_ambient
      real mass_salt,mass_water
c
      real collision_efficiency
c
      double precision ribbon_width
c
      real mean_free_path,dyn_visc
c
c     Cunningham slip variables:
c     real y,alpha,cunningham_slip
      double precision y,alpha,cunningham_slip
c
c     Intermediate terms:
      double precision psi,qc,tc,s1,s2
c
      common /ranz_wong_stuff/ mean_free_path,dyn_visc
c
c     Data statements:
c
      data ribbon_width /6.35e-3/
c     Perry and Hilton, Chem. Eng. Handbook:
      data density_salt /2.163e3/
c
c 
c
      write(*,*) '================================================='
      write(*,*) 'ranz_wong: entry'
      write(*,*) 'ranz_wong: pressure      =',pressure
      write(*,*) 'ranz_wong: temperature   =',temperature
      write(*,*) 'ranz_wong: air_density   =',air_density
      write(*,*) 'ranz_wong: true_air_speed=',true_air_speed
      write(*,*) 'ranz_wong: radius_dry    =',radius_dry
      write(*,*) 'ranz_wong: radius_ambient=',radius_ambient
      write(*,*) '================================================='
      write(4,*) '================================================='
      write(4,*) 'ranz_wong: entry'
      write(4,*) 'ranz_wong: pressure      =',pressure
      write(4,*) 'ranz_wong: temperature   =',temperature
      write(4,*) 'ranz_wong: air_density   =',air_density
      write(4,*) 'ranz_wong: true_air_speed=',true_air_speed
      write(4,*) 'ranz_wong: radius_dry    =',radius_dry
      write(4,*) 'ranz_wong: radius_ambient=',radius_ambient
      write(4,*) '================================================='
c
c
c     Calculate particle density, assuming ideal conditions:
      volume_salt=pi43*radius_dry**3
      mass_salt=volume_salt*density_salt
      volume_ambient=pi43*radius_ambient**3
      volume_water=volume_ambient-volume_salt
      mass_water=volume_water*1.e3
      particle_density=(mass_salt+mass_water)/volume_ambient
      write(*,*) 'ranz_wong: particle_density=',particle_density
c
c     Cunningham slip correction factor: (Pruppacher and Keltt, eq.
c     12.16):
      y=-1.10*radius_ambient/mean_free_path
      write(*,*) 'ranz_wong: y=',y
      alpha=1.257+0.400*dexp(y)
      write(*,*) 'ranz_wong: alpha=',alpha
      cunningham_slip=1.+alpha*mean_free_path/radius_ambient
      write(*,*) 'ranz_wong: cunningham_slip=',cunningham_slip
c     if(y.lt.20.) then
c       cunningham_slip=1.+1.257*mean_free_path/radius_ambient*
c    c   (1.257+0.4*exp(-y))
c     else
c       cunningham_slip=1.+2.*mean_free_path/radius_ambient
c     endif
      write(*,*) 'ranz_wong: cunningham_slip =',cunningham_slip
c
c     Terms in Ranz and Wong paper:
c     CHECK:
      psi=cunningham_slip*particle_density*
     c true_air_speed*(2.*radius_ambient)**2./
     c (18.*dyn_visc*ribbon_width)
      write(*,*) 'ranz_wong: psi             =',psi
c
c     No impaction if psi<1/8:
      if(psi.lt.0.125) then
        collision_efficiency=0.
      else
        qc=sqrt(0.5/psi-1./(16.*psi**2.))
        tc=1./qc*atan(4.*psi*qc/(4.*psi-1.))
        s1=-0.25/psi+sqrt(1./(16.*psi**2.)+0.5/psi)
        s2=-0.25/psi-sqrt(1./(16.*psi**2.)+0.5/psi)
        collision_efficiency=(s2-s1)/(s2*exp(s1*tc)-s1*exp(s2*tc))
      write(*,*) 'ranz_wong: qc                  =',qc
      write(*,*) 'ranz_wong: tc                  =',tc
      write(*,*) 'ranz_wong: s1                  =',s1
      write(*,*) 'ranz_wong: s2                  =',s2
      write(*,*) 'ranz_wong: collision_efficiency=',collision_efficiency
      write(4,*) 'ranz_wong: collision_efficiency=',collision_efficiency
      endif
c
c
      return
      end
