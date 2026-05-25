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
    ! Función: is_overlapping
    !
    ! Verifica si una posición propuesta se superpone con cualquier
    ! con alguna partícula existente.
    !
    ! Parámetros:
    !   sys: sistema de partículas
    !   x_new, y_new: posición a verificar
    !   up_to_idx: solo verificar hasta esta partícula (para inicialización)
    !
    ! Retorna:
    !   .true. si hay superposición, .false. si es válida
    !===========================================================================
    function is_overlapping(sys, x_new, y_new, up_to_idx) result(overlap)
        type(particle_system), intent(in) :: sys
        real(dp), intent(in) :: x_new, y_new
        integer, intent(in), optional :: up_to_idx
        logical :: overlap
        integer :: i, i_max
        real(dp) :: dx, dy, dist_sq
        
        overlap = .false.
        
        ! Determinar hasta qué partícula verificar
        if (present(up_to_idx)) then
            i_max = up_to_idx
        else
            i_max = sys%n
        end if
        
        do i = 1, i_max
            ! Calcular distancia al cuadrado (evitar sqrt para eficiencia)
            dx = x_new - sys%x(i)
            dy = y_new - sys%y(i)
            dist_sq = dx*dx + dy*dy
            
            ! Verificar si la distancia es menor que EPSILON_SOFT (superposición)
            if (dist_sq < EPSILON_SOFT*EPSILON_SOFT) then
                overlap = .true.
                return
            end if
        end do
        
    end function is_overlapping

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

        ! Generar posiciones y cargas como dipolos
        block
            real(dp) :: grid_spacing, rnd1, rnd2
            integer :: idx_grid, i, attempts
            logical :: valid_position
            
            grid_spacing = (2.0_dp * L_DOMAIN) / real(GRID_RESOLUTION - 1, dp)
            
            ! Si modo 2, cargas aleatorias +1 y -1 con mínimo de separación
            if (CHARGE_MODE == 2) then
                ! Asegurar que el número de partículas sea par
                sys%n = sys%n - mod(sys%n, 2)
                
                do i = 1, sys%n
                    ! PRIMERO: GENERAR POSICIÓN ALEATORIA, AJUSTAR A MALLA, VERIFICAR NO SUPERPONGA
                    attempts = 0
                    valid_position = .false.
                    
                    do while (.not. valid_position .and. attempts < 1000)
                        attempts = attempts + 1
                        
                        ! Generar posición aleatoria
                        call random_number(rnd1)
                        call random_number(rnd2)
                        sys%x(i) = -L_DOMAIN + 2.0_dp * L_DOMAIN * rnd1
                        sys%y(i) = -L_DOMAIN + 2.0_dp * L_DOMAIN * rnd2
                        
                        ! Ajustar a la malla
                        idx_grid = nint((sys%x(i) + L_DOMAIN) / grid_spacing)
                        idx_grid = max(0, min(GRID_RESOLUTION - 1, idx_grid))
                        sys%x(i) = -L_DOMAIN + real(idx_grid, dp) * grid_spacing
                        
                        idx_grid = nint((sys%y(i) + L_DOMAIN) / grid_spacing)
                        idx_grid = max(0, min(GRID_RESOLUTION - 1, idx_grid))
                        sys%y(i) = -L_DOMAIN + real(idx_grid, dp) * grid_spacing
                        
                        ! Seguridad extra: garantizar que las coordenadas estén dentro del dominio
                        sys%x(i) = max(-L_DOMAIN, min(L_DOMAIN, sys%x(i)))
                        sys%y(i) = max(-L_DOMAIN, min(L_DOMAIN, sys%y(i)))
                        
                        ! Verificar que no se superponga con partículas anteriores
                        if (i > 1) then
                            if (.not. is_overlapping(sys, sys%x(i), sys%y(i), up_to_idx=i-1)) then
                                valid_position = .true.
                            end if
                        else
                            ! Primera partícula, siempre válida
                            valid_position = .true.
                        end if
                    end do
                    
                    ! Asignar carga: primera mitad +1, segunda mitad -1
                    if (i <= sys%n / 2) then
                        sys%q(i) = 1.0_dp
                    else
                        sys%q(i) = -1.0_dp
                    end if
                end do
                
                ! SEGUNDO: BARAJAR (SHUFFLE) LAS CARGAS PARA QUE SEAN ALEATORIAS!
                block
                    integer :: k, j
                    real(dp) :: temp_q
                    real(dp) :: r
                    
                    do k = sys%n, 2, -1
                        ! Generar índice aleatorio entre 1 y k
                        call random_number(r)
                        j = int(r * real(k, dp)) + 1
                        if (j > k) j = k
                        
                        ! Intercambiar las cargas de las posiciones k y j
                        temp_q = sys%q(k)
                        sys%q(k) = sys%q(j)
                        sys%q(j) = temp_q
                    end do
                end block
                
            else
                ! Modo 1: Todas las cargas positivas
                do i = 1, sys%n
                    call random_number(rnd1)
                    sys%x(i) = -L_DOMAIN + 2.0_dp * L_DOMAIN * rnd1
                    
                    call random_number(rnd2)
                    sys%y(i) = -L_DOMAIN + 2.0_dp * L_DOMAIN * rnd2
                    
                    ! Ajustar a la malla
                    idx_grid = nint((sys%x(i) + L_DOMAIN) / grid_spacing)
                    idx_grid = max(0, min(GRID_RESOLUTION - 1, idx_grid))
                    sys%x(i) = -L_DOMAIN + real(idx_grid, dp) * grid_spacing
                    
                    idx_grid = nint((sys%y(i) + L_DOMAIN) / grid_spacing)
                    idx_grid = max(0, min(GRID_RESOLUTION - 1, idx_grid))
                    sys%y(i) = -L_DOMAIN + real(idx_grid, dp) * grid_spacing
                    
                    sys%x(i) = max(-L_DOMAIN, min(L_DOMAIN, sys%x(i)))
                    sys%y(i) = max(-L_DOMAIN, min(L_DOMAIN, sys%y(i)))
                    
                    sys%q(i) = 1.0_dp
                end do
            end if
        end block

        ! Energía inicial será calculada por mod_energy
        sys%total_energy = 0.0_dp

    end subroutine initialize_system

end module mod_types
