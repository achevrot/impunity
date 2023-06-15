// Compilation: fsharpc units.fs
// Execution: mono units.exe (Linux)

[<Measure>] type meter
[<Measure>] type second

let speed (distance: float<meter>) (duration: float<second>) =
    distance / duration

[<EntryPoint>]
let main argv =
    let distance = 12.<meter>
    let duration = 4.<second>
    let value = speed distance duration
    printfn "Speed: %f m/s" value
    0
