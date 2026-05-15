!===============================================================================
! mod_performance.f90
! Módulo de Rendimiento y Benchmarks
!
! Responsabilidad:
!   - Medir tiempo de ejecución de secciones del código
!   - Almacenar métricas de rendimiento
!   - Generar reportes de benchmarks
!   - Caché para valores calculados frecuentemente
!
! Autor: Proyecto Física II — Universidad Cooperativa de Colombia
!===============================================================================
module mod_performance
    use mod_constants
    implicit none

    private
    public :: timer_start, timer_stop, get_elapsed_time, reset_timer
    public :: performance_report, cache_put, cache_get, cache_clear

    !===========================================================================
    ! Tipo de dato para el caché de valores calculados
    !===========================================================================
    type, private :: cache_entry
        real(dp) :: key1, key2
        real(dp) :: value
        logical  :: valid = .false.
    end type cache_entry

    !===========================================================================
    ! Variables globales privadas
    !===========================================================================
    real(dp), private, save :: start_time = 0.0_dp
    real(dp), private, save :: total_time = 0.0_dp
    integer,  private, save :: n_calls = 0

    ! Caché simple (para valores frecuentes)
    integer, parameter, private :: CACHE_SIZE = 1000
    type(cache_entry), private, save :: cache(CACHE_SIZE)

contains

    !===========================================================================
    ! SUBRUTINA: timer_start
    !
    ! Inicia el cronómetro para medir tiempo de ejecución
    !===========================================================================
    subroutine timer_start()
        implicit none
        call cpu_time(start_time)
    end subroutine timer_start

    !===========================================================================
    ! SUBRUTINA: timer_stop
    !
    ! Detiene el cronómetro y acumula el tiempo transcurrido
    !===========================================================================
    subroutine timer_stop()
        implicit none
        real(dp) :: end_time
        call cpu_time(end_time)
        total_time = total_time + (end_time - start_time)
        n_calls = n_calls + 1
    end subroutine timer_stop

    !===========================================================================
    ! FUNCIÓN: get_elapsed_time
    !
    ! Devuelve el tiempo total transcurrido en segundos
    !===========================================================================
    function get_elapsed_time() result(time)
        implicit none
        real(dp) :: time
        time = total_time
    end function get_elapsed_time

    !===========================================================================
    ! SUBRUTINA: reset_timer
    !
    ! Reinicia el contador de tiempo
    !===========================================================================
    subroutine reset_timer()
        implicit none
        start_time = 0.0_dp
        total_time = 0.0_dp
        n_calls = 0
    end subroutine reset_timer

    !===========================================================================
    ! SUBRUTINA: cache_put
    !
    ! Almacena un valor en el caché con una clave simple
    !===========================================================================
    subroutine cache_put(key1, key2, value)
        implicit none
        real(dp), intent(in) :: key1, key2, value
        integer :: idx

        ! Búsqueda simple de índice (hash trivial)
        idx = mod(int(abs(key1 * 1000 + key2 * 1000)), CACHE_SIZE) + 1

        ! Almacenar en caché
        cache(idx)%key1 = key1
        cache(idx)%key2 = key2
        cache(idx)%value = value
        cache(idx)%valid = .true.
    end subroutine cache_put

    !===========================================================================
    ! FUNCIÓN: cache_get
    !
    ! Recupera un valor del caché. Devuelve .true. si fue encontrado.
    !===========================================================================
    function cache_get(key1, key2, value) result(found)
        implicit none
        real(dp), intent(in)  :: key1, key2
        real(dp), intent(out) :: value
        logical               :: found
        integer :: idx

        idx = mod(int(abs(key1 * 1000 + key2 * 1000)), CACHE_SIZE) + 1

        if (cache(idx)%valid .and. &
            abs(cache(idx)%key1 - key1) < 1e-10_dp .and. &
            abs(cache(idx)%key2 - key2) < 1e-10_dp) then
            value = cache(idx)%value
            found = .true.
        else
            found = .false.
        end if
    end function cache_get

    !===========================================================================
    ! SUBRUTINA: cache_clear
    !
    ! Limpia todo el caché
    !===========================================================================
    subroutine cache_clear()
        implicit none
        integer :: i
        do i = 1, CACHE_SIZE
            cache(i)%valid = .false.
        end do
    end subroutine cache_clear

    !===========================================================================
    ! SUBRUTINA: performance_report
    !
    ! Genera un reporte de rendimiento completo
    !===========================================================================
    subroutine performance_report()
        implicit none
        write(*,*)
        write(*,*) "============================================="
        write(*,*) "       REPORTE DE RENDIMIENTO"
        write(*,*) "============================================="
        write(*,*) "Número de mediciones: ", n_calls
        write(*,*) "Tiempo total acumulado: ", total_time, " s"
        if (n_calls > 0) then
            write(*,*) "Tiempo promedio por llamada: ", total_time / real(n_calls, dp), " s"
        end if
        write(*,*) "============================================="
        write(*,*)
    end subroutine performance_report

end module mod_performance
