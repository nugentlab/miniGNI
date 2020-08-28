      subroutine const
c
c     Set all physical constants which do not severely depend on temp.
c
c     All units are MKSA.
c
c     This subroutine must be called immediately after start up of the
c     main program. All subsequent subroutines which uses these
c     constants must have "include file" "const_com.h" present.
c
      include 'const_com.h'
c
c     Heat capacity of dry air:
      data cpd/1004.6/
c
c     Ideal gas constant :
      data r_ideal/8314.51/
c
c     Gas constant for dry air:
      data rd/287.04/
c
c     Mean molar mass of dry air(g/mol)
      data md/28.965/
c
c     Gas constant for water vapor
      data rv/461.50/
c
c     Mean molar mass of water vapor(g/mol)
      data mv/18.0153/
c
c     Ratio of gas constants for dry air and water vapor:
      data epsilo/0.62198/
c
c     Gravity acceleration:
      data g/9.80/
c
c     Convert from Celcius to Kelvin:
      data t_offset/273.16/
c
c     Pi:
      data pi/3.1415926/
c
c     2 Pi:
      data pi2/6.2831853/
c
c     4/3 Pi:
      data pi43/4.1887902/
c
c     heat capacity of liquid water
      data cw/4218./
c
c     heat capacity of water vapor
      data cpv/1875./
c
c     density of water
      data rhow/1.e3/
c
c     Latent heat of vaporization:
      data xlatent/2.5e6/
c
c     Stefan Bolzman's constant:
      data boltzman /5.67e-8/
c
c     Solar constant:
      data solar_constant /1373./
c
c     Go from degrees to radians, single precision:
      deg_to_rad=180./acos(-1.)
c
c     Go from degrees to radians, double precision:
      ddeg_to_rad=180./acos(-1.)
c
      return
      end
