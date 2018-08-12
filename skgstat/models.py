import math
from functools import wraps

import numpy as np
from scipy import special
from numba import jit


def variogram(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if hasattr(args[0], '__iter__'):
            new_args = args[1:]
            mapping = map(lambda h: func(h, *new_args, **kwargs), args[0])
            return np.fromiter(mapping, dtype=float)
        else:
            return func(*args, **kwargs)
    return wrapper


@variogram
@jit
def spherical(h, r, c0, b=0):
    r"""Spherical Variogram function

    Implementation of the spherical variogram function. Calculates the
    dependent variable for a given lag (h). The nugget (b) defaults to be 0.

    Parameters
    ----------
    h : float
        Specifies the lag of separating distances that the dependent variable
        shall be calculated for. It has to be a positive real number.
    r : float
        The effective range. Note this is not the range parameter! However,
        for the spherical variogram the range and effective range are the same.
    c0 : float
        The sill of the variogram, where it will flatten out. The function
        will not return a value higher than C0 + b.
    b : float
        The nugget of the variogram. This is the value of independent
        variable at the distance of zero. This is usually attributed to
        non-spatial variance.

    Returns
    -------
    gamma : numpy.float64
        Unlike in most variogram function formulas, which define the function
        for :math:`2*\gamma`, this function will return :math:`\gamma` only.

    Notes
    -----
    The implementation follows _[10]:

    .. math::
        \gamma = b + C_0 * \left({1.5*\frac{h}{r} - 0.5*{\frac{h}{r]^3}\right)

    if :math:`h < r`, and

    .. math::
        \gamma = b + C_0

    else. r is the effective range, which is in case of the spherical
    variogram just a.

    References
    ----------
    .. [10]: Burgess, T. M., & Webster, R. (1980). Optimal interpolation
       and isarithmic mapping of soil properties. I.The semi-variogram and
       punctual kriging. Journal of Soil and Science, 31(2), 315–331,
       http://doi.org/10.1111/j.1365-2389.1980.tb02084.x

    """
    # prepare parameters
    a = r / 1.

    if h <= r:
        return b + c0 * ((1.5 * (h / a)) - (0.5 * ((h / a) ** 3.0)))
    else:
        return b + c0


@variogram
@jit
def exponential(h, r, c0, b=0):
    r"""Exponential Variogram function

    Implementation of the exponential variogram function. Calculates the
    dependent variable for a given lag (h). The nugget (b) defaults to be 0.

    Parameters
    ----------
    h : float
        Specifies the lag of separating distances that the dependent variable
        shall be calculated for. It has to be a positive real number.
    r : float
        The effective range. Note this is not the range parameter! For the
        exponential variogram function the range parameter a is defined to be
        :math:`a=\frac{r}{3}`. The effective range is the lag where 95% of the
        sill are exceeded. This is needed as the sill is only approached
        asymptotically by an exponential function.
    c0 : float
        The sill of the variogram, where it will flatten out. The function
        will not return a value higher than C0 + b.
    b : float
        The nugget of the variogram. This is the value of independent
        variable at the distance of zero. This is usually attributed to
        non-spatial variance.

    Returns
    -------
    gamma : numpy.float64
        Unlike in most variogram function formulas, which define the function
        for :math:`2*\gamma`, this function will return :math:`\gamma` only.

    Notes
    -----
    The implementation following _[11] and _[12] is as:
    .. math::
        \gamma = b + C_0 * \left({1 - e^{-\frac{h}{a}}}\right)

    a is the range parameter, that can be calculated from the
    effective range r as: :math:`a = \frac{r}{3}`.

    References
    ----------

    .. [11]: Cressie, N. (1993): Statistics for spatial data.
       Wiley Interscience.

    .. [12]: Chiles, J.P., Delfiner, P. (1999). Geostatistics. Modeling Spatial
       Uncertainty. Wiley Interscience.

    """
    # prepare parameters
    a = r / 3.

    return b + c0 * (1. - math.exp(-(h / a)))


@variogram
@jit
def gaussian(h, r, c0, b=0):
    """ Gaussian Variogram function

    Implementation of the Gaussian variogram function. Calculates the
    dependent variable for a given lag (h). The nugget (b) defaults to be 0.

    Parameters
    ----------
    h : float
        Specifies the lag of separating distances that the dependent variable
        shall be calculated for. It has to be a positive real number.
    r : float
        The effective range. Note this is not the range parameter! For the
        exponential variogram function the range parameter a is defined to be
        :math:`a=\frac{r}{3}`. The effetive range is the lag where 95% of the
        sill are exceeded. This is needed as the sill is only approached
        asymptotically by an exponential function.
    c0 : float
        The sill of the variogram, where it will flatten out. The function
        will not return a value higher than C0 + b.
    b : float
        The nugget of the variogram. This is the value of independent
        variable at the distance of zero. This is usually attributed to
        non-spatial variance.

    Returns
    -------
    gamma : numpy.float64
        Unlike in most variogram function formulas, which define the function
        for :math:`2*\gamma`, this function will return :math:`\gamma` only.

    Notes
    -----

    This implementation follows _[12]:
    .. math::
        \gamma = b + c_0 * \left({1 - e^{-\frac{h^2}{a^2}}}\right)

    a is the range parameter, that can be calculated from the
    effective range r as: :math:`a = \frac{r}{2}`.

    References
    ----------

    .. [12]: Chiles, J.P., Delfiner, P. (1999). Geostatistics. Modeling Spatial
       Uncertainty. Wiley Interscience.

    """
    # prepare parameters
    a = r / 2.

    return b + c0 * (1. - math.exp(- (h ** 2 / a ** 2)))


@variogram
@jit
def cubic(h, r, c0, b=0):
    """Cubic Variogram function

    Implementation of the Cubic variogram function. Calculates the
    dependent variable for a given lag (h). The nugget (b) defaults to be 0.

    Parameters
    ----------
    h : float
        Specifies the lag of separating distances that the dependent variable
        shall be calculated for. It has to be a positive real number.
    r : float
        The effective range. Note this is not the range parameter! However,
        for the cubic variogram the range and effective range are the same.
    c0 : float
        The sill of the variogram, where it will flatten out. The function
        will not return a value higher than C0 + b.
    b : float
        The nugget of the variogram. This is the value of independent
        variable at the distance of zero. This is usually attributed to
        non-spatial variance.

    Returns
    -------
    gamma : numpy.float64
        Unlike in most variogram function formulas, which define the function
        for :math:`2*\gamma`, this function will return :math:`\gamma` only.

    Notes
    -----

    This implementation is like:
    .. math::

        \gamma = b + c_0 *  \left[{
                    7    * \left(\frac{h^2}{a^2}\right) -
            \frac{35}{4} * \left(\frac{h^3}{a^3}\right) +
            \frac{7}{2}  * \left(\frac{h^5}{a^5}\right) -
            \frac{3}{4}  * \left(\frac{h^7}{a^7}\right)
            ]\right]

    a is the range parameter. For the cubic function, the effective range and
    range parameter are the same.

    """
    # prepare parameters
    a = r / 1.

    if h <= r:
        return b + c0 * ((7 * (h ** 2 / a ** 2)) -
                         ((35 / 4) * (h ** 3 / a ** 3)) +
                         ((7 / 2) * (h ** 5 / a ** 5)) -
                         ((3 / 4) * (h ** 7 / a ** 7)))
    else:
        return b + c0


@variogram
@jit
def stable(h, r, c0, s, b=0):
    r"""Stable Variogram function

    Implementation of the stable variogram function. Calculates the
    dependent variable for a given lag (h). The nugget (b) defaults to be 0.

    Parameters
    ----------
    h : float
        Specifies the lag of separating distances that the dependent variable
        shall be calculated for. It has to be a positive real number.
    r : float
        The effective range. Note this is not the range parameter! For the
        stable variogram function the range parameter a is defined to be
        :math:`a = \frac{r}{3^{\frac{1}{s}}}`. The effective range is the lag
        where 95% of the sill are exceeded. This is needed as the sill is
        only approached asymptotically by the e-function part of the stable
        model.
    c0 : float
        The sill of the variogram, where it will flatten out. The function
        will not return a value higher than C0 + b.
    s : float
        Shape parameter. For s <= 2 the model will be shaped more like a
        exponential or spherical model, for s > 2 it will be shaped most like
        a Gaussian function.
    b : float
        The nugget of the variogram. This is the value of independent
        variable at the distance of zero. This is usually attributed to
        non-spatial variance.

    Returns
    -------
    gamma : numpy.float64
        Unlike in most variogram function formulas, which define the function
        for :math:`2*\gamma`, this function will return :math:`\gamma` only.

    Notes
    -----
    The implementation is:

    .. math::
        \gamma = b + C_0 * \left({1. - e^{- {\frac{h}{a}}^s}}\right)

    a is the range parameter and is calculated from the effective range r as:

    .. math::
        a = \frac{r}{3^{\frac{1}{s}}}

    """
    # prepare parameters
    a = r / np.power(3, 1 / s)

#    if s > 2:
#        s = 2
    return b + c0 * (1. - math.exp(- math.pow(h / a, s)))


@variogram
@jit
def matern(h, r, c0, s, b=0):
    r"""Matérn Variogram function

    Implementation of the Matérn variogram function. Calculates the
    dependent variable for a given lag (h). The nugget (b) defaults to be 0.

    Parameters
    ----------
    h : float
        Specifies the lag of separating distances that the dependent variable
        shall be calculated for. It has to be a positive real number.
    r : float
        The effective range. Note this is not the range parameter! For the
        Matérn variogram function the range parameter a is defined to be
        :math:`a = \frac{r}{2}`. The effective range is the lag
        where 95% of the sill are exceeded. This is needed as the sill is
        only approached asymptotically by Matérn model.
    c0 : float
        The sill of the variogram, where it will flatten out. The function
        will not return a value higher than C0 + b.
    s : float
        Smoothness parameter. The smoothness parameter can shape a smooth or
        rough variogram function. A value of 0.5 will yield the exponential
        function, while a smoothness of +inf is exactly the Gaussian model.
        Typically a value of 10 is close enough to Gaussian shape to simulate
        its behaviour. Low values are considered to be 'smooth', while larger
        values are considered to describe a 'rough' random field.
    b : float
        The nugget of the variogram. This is the value of independent
        variable at the distance of zero. This is usually attributed to
        non-spatial variance.

    Returns
    -------
    gamma : numpy.float64
        Unlike in most variogram function formulas, which define the function
        for :math:`2*\gamma`, this function will return :math:`\gamma` only.

    Notes
    -----
    The formula and references will follow.

    """
    # prepare parameters
    # TODO: depend a on s, for 0.5 should be 3, above 10 should be 3
    a = r / 2.

    # calculate
    return b + c0 * (1. - (2 / special.gamma(s)) *
                     np.power((h * np.sqrt(s)) / a, s) *
                     special.kv(s, 2 * ((h * np.sqrt(s)) / a))
                     )
