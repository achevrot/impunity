let distance : <m> dfloat = create 12. and time : <s> dfloat = create 4.
let speed distance time = distance /: time
(* val speed: <m> Dim.dfloat -> <s> Dim.dfloat -> <m / s> Dim.dfloat = fun *)

let foot : <m/ft> dfloat = create 0.3048
let feet_to_meters (x : <ft> dfloat) = x *: foot
