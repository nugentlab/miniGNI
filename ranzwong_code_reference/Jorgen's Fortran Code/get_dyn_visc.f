      subroutine get_dyn_visc(temperature,dyn_visc)
c
c     Calculate dynamic viscosity as a function of temperature.
c     Source: pruppacher and Klett, p323, eq. 10-107.
c
      real dyn_visc
      real temperature
c
c
c     Dynamic viscosity of air, pruppacher and klett, eq (10-107a)
      if(temperature.ge.273.16) then
        dyn_visc=1.718e-5+4.9e-8*(temperature-273.16)
      else
        dyn_visc=1.718e-5+4.9e-8*(temperature-273.16)-1.2e-10*
     c   (temperature-273.16)**2
      endif
c
      return
      end
