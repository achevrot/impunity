from typing import TypeVar

from typing_extensions import Annotated  # ①

import numpy as np
from impunity import impunity

GAMMA: Annotated[float, "dimensionless"] = 1.40  # ②
R: Annotated[float, "m^2 / (s^2 * C)"] = 287.05287
STRATOSPHERE_TEMP: Annotated[float, "K"] = 216.65


F = TypeVar("F", float, np.ndarray)  # ③


@impunity
def temperature(h: Annotated[F, "m"]) -> Annotated[F, "K"]:
    """Temperature of ISA atmosphere

    :param h: the altitude (by default in meters), :math:`0 < h < 84852`
        (will be clipped when outside range, integer input allowed)

    :return: the temperature (in K)

    """

    temp_0: Annotated[float, "K"] = 288.15
    c: Annotated[float, "K/m"] = 0.0065
    temp: Annotated[F, "K"] = np.maximum(  # ④
        temp_0 - c * h,  # ⑤
        STRATOSPHERE_TEMP,
    )
    return temp


@impunity(rewrite="sound_speed.py")  # ⑥
def sound_speed(h: Annotated[F, "ft"]) -> Annotated[F, "kts"]:
    """Speed of sound in ISA atmosphere

    :param h: the altitude (by default in feet), :math:`0 < h < 84852`
        (will be clipped when outside range, integer input allowed)

    :return: the speed of sound :math:`a`, in m/s

    """
    temp = temperature(h)  # ⑦
    a: Annotated[F, "m/s"] = np.sqrt(GAMMA * R * temp)  # ⑧
    return a


@impunity  # ⑨
def main() -> None:
    altitude: "m" = 1000
    print(sound_speed(altitude))  # ⑩ a.
    # 653.9753225425684

    altitude_array: "ft" = np.array([0, 3280.84, 5000, 10000, 30000])
    x = sound_speed(altitude_array)  # ⑩ b.
    print(x)
    # [661.47859444 653.9753223  650.00902555 638.3334048  589.32227624]

    y: "m/s" = sound_speed(altitude_array)  # ⑩ c.
    print(y)
    # [340.29398803 336.43397136 334.39353203 328.3870738  303.173571  ]

    temperature_array: "degC" = temperature(altitude_array)  # ⑩
    print(temperature_array)
    # [ 15.           8.49999979   5.094       -4.812      -44.436     ]


if __name__ == "__main__":
    main()
