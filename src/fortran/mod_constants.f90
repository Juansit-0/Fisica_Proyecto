!===============================================================================
! mod_constants.f90
! Módulo de constantes físicas y parámetros de simulación
!
! Responsabilidad: Centralizar todas las constantes del sistema para
! garantizar consistencia y facilitar la parametrización.
!
! Diseño: Uso de parámetros de compilación (parameter) para constantes
! universales, y variables configurables para parámetros de simulación
! que se leen desde archivo de entrada.
!
! Autor: Proyecto Física II — Universidad Cooperativa de Colombia
!===============================================================================
module mod_constants
    implicit none

    ! =========================================================================
    ! Precisión numérica
    ! =========================================================================
    ! Usamos double precision (real64) para toda la aritmética de punto
    ! flotante. Esto proporciona ~15 dígitos significativos, necesario
    ! para calcular diferencias de energía ΔU con precisión suficiente.
    integer, parameter :: dp = selected_real_kind(15, 307)

    ! =========================================================================
    ! Constantes físicas universales
    ! =========================================================================
    ! Constante de Coulomb k = 8.9875 × 10⁹ N·m²/C²
    ! En unidades naturales para la simulación, k = 1.0 simplifica
    ! los cálculos sin perder generalidad (equivale a medir energía
    ! en unidades de k·e²/L).
    real(dp), parameter :: K_COULOMB = 1.0_dp

    ! Pi — necesario para análisis angulares y distribuciones
    real(dp), parameter :: PI = 3.14159265358979323846_dp

    ! =========================================================================
    ! Parámetros de estabilidad numérica
    ! =========================================================================
    ! Softening parameter ε: previene singularidad cuando r→0
    ! |r_eff| = sqrt(dx² + dy² + ε²)
    !
    ! Justificación: En simulaciones N-body, la fuerza de Coulomb diverge
    ! como 1/r cuando dos partículas se acercan. El softening introduce
    ! un radio mínimo efectivo sin alterar la física a distancias r >> ε.
    !
    ! Valor: ε = 1.0e-2 es suficientemente pequeño comparado con L=10
    ! (ε/L = 0.001) para no distorsionar las interacciones, pero
    ! suficientemente grande para evitar overflow/NaN.
    real(dp), parameter :: EPSILON_SOFT = 1.0e-2_dp

    ! =========================================================================
    ! Parámetros de simulación (configurables desde archivo)
    ! =========================================================================
    ! Estos parámetros se leen desde data/input/simulation_params.txt
    ! Los valores aquí son defaults que se sobreescriben.

    ! Número máximo de partículas soportado (para dimensionamiento estático)
    integer, parameter :: MAX_PARTICLES = 200

    ! Valores default (sobreescritos por archivo de parámetros)
    integer  :: N_PARTICLES  = 50       ! Número de partículas
    real(dp) :: L_DOMAIN     = 10.0_dp  ! Medio-lado del dominio [-L, L]²
    real(dp) :: DELTA_MOVE   = 0.25_dp  ! Tamaño máximo del paso aleatorio
    integer  :: MAX_ITER     = 500000   ! Iteraciones máximas
    integer  :: SAVE_EVERY   = 1        ! Guardar configuración cada N aceptaciones
    integer  :: PRINT_EVERY  = 10000    ! Imprimir progreso cada N iteraciones
    integer  :: GRID_RESOLUTION = 50   ! Puntos por lado de la malla

    ! Modo de cargas:
    !   1 = solo positivas (+1)
    !   2 = mezcla aleatoria (+1 y -1)
    integer  :: CHARGE_MODE  = 1

    ! Semilla para generador aleatorio (0 = usar clock del sistema)
    integer  :: SEED_VALUE  = 0

end module mod_constants
