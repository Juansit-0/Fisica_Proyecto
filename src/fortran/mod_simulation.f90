!===============================================================================
! mod_simulation.f90
! Módulo del algoritmo de minimización energética
!
! Responsabilidad: Implementar el loop principal de simulación con el
! algoritmo greedy de minimización:
!   1. Seleccionar partícula aleatoria
!   2. Proponer movimiento aleatorio δ
!   3. Verificar límites del dominio
!   4. Calcular ΔU (cambio en energía)
!   5. Aceptar SOLO si ΔU < 0
!
! Relación con métodos conocidos:
!   Este algoritmo es un caso particular de Monte Carlo con T=0
!   (temperatura cero), equivalente a un descenso de gradiente
!   estocástico sin momentum. A diferencia de simulated annealing,
!   NUNCA acepta movimientos que aumenten la energía.
!
!   Ventaja: convergencia garantizada (energía monótonamente decreciente)
!   Desventaja: puede quedar atrapado en mínimos locales
!
! Autor: Proyecto Física II — Universidad Cooperativa de Colombia
!===============================================================================
module mod_simulation
    use mod_constants
    use mod_types
    use mod_energy
    use mod_io
    implicit none

contains

    !===========================================================================
    ! Subrutina: run_simulation
    !
    ! Ejecuta el algoritmo completo de minimización energética.
    !
    ! Algoritmo detallado:
    !   FOR iter = 1 TO MAX_ITER:
    !     1. idx = random_integer(1, N)         ! Partícula aleatoria
    !     2. δx = random(-DELTA, +DELTA)        ! Desplazamiento aleatorio
    !        δy = random(-DELTA, +DELTA)
    !     3. x_new = x(idx) + δx
    !        y_new = y(idx) + δy
    !     4. IF x_new ∉ [-L,L] OR y_new ∉ [-L,L]:
    !          REJECT (fuera de dominio)
    !          CONTINUE
    !     5. ΔU = compute_delta_energy(sys, idx, x_new, y_new)
    !     6. IF ΔU < 0:
    !          x(idx) = x_new
    !          y(idx) = y_new
    !          U_total += ΔU
    !          accepted_moves++
    !          IF mod(accepted_moves, SAVE_EVERY) == 0:
    !            save_configuration(sys)
    !        ELSE:
    !          rejected_moves++
    !
    ! Complejidad total: O(MAX_ITER × N) = O(500000 × 50) = O(25M)
    !
    ! Argumentos:
    !   sys (inout) — Sistema de partículas (modificado in-place)
    !===========================================================================
    subroutine run_simulation(sys)
        type(particle_system), intent(inout) :: sys

        integer  :: iter, idx, config_count
        real(dp) :: rnd, dx, dy, x_new, y_new
        real(dp) :: delta_u, acceptance_rate

        ! Contadores
        config_count = 0

        ! Calcular energía inicial
        sys%total_energy = compute_total_energy(sys)

        write(*,'(A)')         ''
        write(*,'(A)')         '  =============================================='
        write(*,'(A)')         '  INICIANDO SIMULACION'
        write(*,'(A)')         '  =============================================='
        write(*,'(A,ES14.6)')  '  Energia inicial     = ', sys%total_energy
        write(*,'(A)')         ''

        ! Guardar configuración inicial como frame 0
        config_count = config_count + 1
        call save_configuration(sys, config_count, 'data/output/configurations')

        ! Registrar energía inicial
        call write_energy_log(0, 0, sys%total_energy, 0.0_dp)

        ! =====================================================================
        ! LOOP PRINCIPAL DE MINIMIZACIÓN
        ! =====================================================================
        do iter = 1, MAX_ITER

            ! -----------------------------------------------------------------
            ! Paso 1: Seleccionar partícula aleatoria
            ! -----------------------------------------------------------------
            ! Generar índice aleatorio en [1, N]
            call random_number(rnd)
            idx = int(rnd * sys%n) + 1
            ! Clamp para evitar índice fuera de rango por rnd = 1.0
            if (idx > sys%n) idx = sys%n

            ! -----------------------------------------------------------------
            ! Paso 2: Generar desplazamiento aleatorio
            ! -----------------------------------------------------------------
            ! δx, δy ∈ [-DELTA_MOVE, +DELTA_MOVE] (distribución uniforme)
            call random_number(rnd)
            dx = (2.0_dp * rnd - 1.0_dp) * DELTA_MOVE

            call random_number(rnd)
            dy = (2.0_dp * rnd - 1.0_dp) * DELTA_MOVE

            ! Nuevas coordenadas propuestas
            x_new = sys%x(idx) + dx
            y_new = sys%y(idx) + dy

            ! -----------------------------------------------------------------
            ! Paso 3: Verificar límites del dominio
            ! -----------------------------------------------------------------
            if (abs(x_new) > L_DOMAIN .or. abs(y_new) > L_DOMAIN) then
                sys%out_of_bounds = sys%out_of_bounds + 1
                sys%rejected_moves = sys%rejected_moves + 1
                cycle  ! Rechazar y continuar con siguiente iteración
            end if

            ! -----------------------------------------------------------------
            ! Paso 4: Calcular cambio en energía ΔU
            ! -----------------------------------------------------------------
            delta_u = compute_delta_energy(sys, idx, x_new, y_new)

            ! -----------------------------------------------------------------
            ! Paso 5: Criterio de aceptación (greedy / T=0)
            ! -----------------------------------------------------------------
            if (delta_u < 0.0_dp) then
                ! ACEPTAR: el movimiento reduce la energía
                sys%x(idx) = x_new
                sys%y(idx) = y_new
                sys%total_energy = sys%total_energy + delta_u
                sys%accepted_moves = sys%accepted_moves + 1

                ! Guardar configuración cada SAVE_EVERY aceptaciones
                if (mod(sys%accepted_moves, SAVE_EVERY) == 0) then
                    config_count = config_count + 1
                    call save_configuration(sys, config_count, 'data/output/configurations')
                end if

                ! Registrar en log de energía
                acceptance_rate = real(sys%accepted_moves, dp) / real(iter, dp)
                call write_energy_log(iter, sys%accepted_moves, sys%total_energy, acceptance_rate)
            else
                ! RECHAZAR: el movimiento no reduce la energía
                sys%rejected_moves = sys%rejected_moves + 1
            end if

            ! -----------------------------------------------------------------
            ! Reporte de progreso
            ! -----------------------------------------------------------------
            if (mod(iter, PRINT_EVERY) == 0) then
                acceptance_rate = real(sys%accepted_moves, dp) / real(iter, dp)
                write(*,'(A,I10,A,I10,A,ES14.6,A,F6.2,A)') &
                    '  Iter: ', iter, &
                    '  Aceptados: ', sys%accepted_moves, &
                    '  U = ', sys%total_energy, &
                    '  Rate = ', acceptance_rate * 100.0_dp, '%'
            end if

        end do  ! Fin del loop principal

        ! =====================================================================
        ! RESUMEN FINAL
        ! =====================================================================
        ! Guardar última configuración como configuración final
        config_count = config_count + 1
        call save_configuration(sys, config_count, 'data/output/configurations')

        acceptance_rate = real(sys%accepted_moves, dp) / real(MAX_ITER, dp)

        write(*,'(A)')         ''
        write(*,'(A)')         '  =============================================='
        write(*,'(A)')         '  SIMULACION COMPLETADA'
        write(*,'(A)')         '  =============================================='
        write(*,'(A,ES14.6)')  '  Energia final       = ', sys%total_energy
        write(*,'(A,I10)')     '  Movimientos aceptados = ', sys%accepted_moves
        write(*,'(A,I10)')     '  Movimientos rechazados= ', sys%rejected_moves
        write(*,'(A,I10)')     '  Fuera de dominio      = ', sys%out_of_bounds
        write(*,'(A,F8.2,A)')  '  Tasa de aceptacion    = ', acceptance_rate * 100.0_dp, '%'
        write(*,'(A,I10)')     '  Configuraciones guardadas = ', config_count
        write(*,'(A)')         '  =============================================='

    end subroutine run_simulation

end module mod_simulation
