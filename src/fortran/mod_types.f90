!===============================================================================
! mod_types.f90
! Módulo de tipos derivados y estructuras de datos
!
! Responsabilidad: Definir la estructura de datos del sistema de partículas
! y proporcionar subrutinas de inicialización.
!
! Diseño: Uso de arrays de tamaño fijo (MAX_PARTICLES) para evitar
! asignación dinámica y mejorar cache locality. El tamaño real del
! sistema está dado por N_PARTICLES.
!
! Autor: Proyecto Física II — Universidad Cooperativa de Colombia
!===============================================================================
module mod_types
    use mod_constants
    implicit none

    ! =========================================================================
    ! Tipo derivado: Sistema de partículas
    ! =========================================================================
    ! Encapsula el estado completo del sistema electrostático:
    ! - Posiciones (x, y) de cada partícula
    ! - Cargas eléctricas q
    ! - Energía total del sistema
    ! - Contadores estadísticos
    !
    ! Nota sobre cache locality: Los arrays x, y, q son contiguos en
    ! memoria, lo que favorece accesos secuenciales en los loops de
    ! cálculo de energía (stride-1 access pattern).
    type :: particle_system
        ! Posiciones de las partículas
        real(dp) :: x(MAX_PARTICLES)
        real(dp) :: y(MAX_PARTICLES)

        ! Cargas eléctricas (+1 o -1)
        real(dp) :: q(MAX_PARTICLES)

        ! Energía electrostática total del sistema
        real(dp) :: total_energy

        ! Número activo de partículas (≤ MAX_PARTICLES)
        integer :: n

        ! Contadores estadísticos
        integer :: accepted_moves   ! Movimientos aceptados (ΔU < 0)
        integer :: rejected_moves   ! Movimientos rechazados (ΔU ≥ 0)
        integer :: out_of_bounds    ! Movimientos fuera del dominio

    end type particle_system

contains

    !===========================================================================
    ! Subrutina: initialize_system
    !
    ! Inicializa el sistema de partículas con posiciones aleatorias
    ! dentro del dominio [-L, L]×[-L, L] y cargas según el modo.
    !
    ! Argumentos:
    !   sys  (out) — Sistema de partículas a inicializar
    !
    ! Modo de cargas:
    !   CHARGE_MODE = 1 → todas las cargas son +1
    !   CHARGE_MODE = 2 → 50% +1, 50% -1 (alternando)
    !
    ! Generación aleatoria:
    !   Usa random_number() intrínseco de Fortran, con semilla
    !   configurable para reproducibilidad.
    !===========================================================================
    subroutine initialize_system(sys)
        type(particle_system), intent(out) :: sys
        real(dp) :: rnd
        integer  :: i
        integer  :: seed_size
        integer, allocatable :: seed_array(:)

        ! Configurar semilla del generador aleatorio
        ! Nota: usamos variable local para evitar colisión con
        ! el intrínseco random_seed
        seed_size = 1
        call random_seed(size=seed_size)
        allocate(seed_array(seed_size))

        if (SEED_VALUE /= 0) then
            ! Semilla determinista para reproducibilidad
            seed_array = SEED_VALUE
            call random_seed(put=seed_array)
        else
            ! Usar clock del sistema para semilla no determinista
            call random_seed()
        end if

        deallocate(seed_array)

        ! Configurar número de partículas
        sys%n = N_PARTICLES

        ! Inicializar contadores
        sys%accepted_moves = 0
        sys%rejected_moves = 0
        sys%out_of_bounds  = 0

        ! Generar posiciones aleatorias en [-L, L]×[-L, L]
        ! Transformación: r = -L + 2L * U[0,1)
        do i = 1, sys%n
            call random_number(rnd)
            sys%x(i) = -L_DOMAIN + 2.0_dp * L_DOMAIN * rnd

            call random_number(rnd)
            sys%y(i) = -L_DOMAIN + 2.0_dp * L_DOMAIN * rnd
        end do

        ! Asignar cargas según modo
        select case (CHARGE_MODE)
        case (1)
            ! Fase 1: Todas las cargas positivas
            do i = 1, sys%n
                sys%q(i) = 1.0_dp
            end do

        case (2)
            ! Fase 2: Mezcla de cargas +1 y -1
            ! Primera mitad positiva, segunda mitad negativa
            do i = 1, sys%n
                if (i <= sys%n / 2) then
                    sys%q(i) = 1.0_dp
                else
                    sys%q(i) = -1.0_dp
                end if
            end do

        case default
            ! Default: todas positivas
            do i = 1, sys%n
                sys%q(i) = 1.0_dp
            end do
        end select

        ! Energía inicial será calculada por mod_energy
        sys%total_energy = 0.0_dp

    end subroutine initialize_system

end module mod_types
