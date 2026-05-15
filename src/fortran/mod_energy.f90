!===============================================================================
! mod_energy.f90
! Módulo de cálculo de energía electrostática
!
! Responsabilidad: Calcular la energía total del sistema y las variaciones
! de energía (ΔU) al mover una partícula individual.
!
! Física implementada:
!   U = k Σ(i<j) qi·qj / |ri - rj|
!
! Optimización clave:
!   En lugar de recalcular U completa O(N²) en cada iteración,
!   calculamos solo ΔU al mover partícula idx, que es O(N).
!   Esto reduce la complejidad por iteración de O(N²) a O(N).
!
! Estabilidad numérica:
!   Se usa softening: |r| = sqrt(dx² + dy² + ε²) para evitar
!   divergencia cuando dos partículas están muy cerca.
!
! Autor: Proyecto Física II — Universidad Cooperativa de Colombia
!===============================================================================
module mod_energy
    use mod_constants
    use mod_types
    implicit none

contains

    !===========================================================================
    ! Función: compute_total_energy
    !
    ! Calcula la energía electrostática total del sistema sumando
    ! sobre todos los pares (i < j).
    !
    ! Complejidad: O(N²/2) — N(N-1)/2 pares
    ! Para N=50: 1225 evaluaciones de pares
    !
    ! Se usa al inicio de la simulación y para verificaciones.
    ! Durante la evolución, se usa compute_delta_energy.
    !
    ! Implementación:
    !   U = k Σ(i=1..N-1) Σ(j=i+1..N) qi·qj / sqrt((xi-xj)² + (yi-yj)² + ε²)
    !===========================================================================
    function compute_total_energy(sys) result(energy)
        type(particle_system), intent(in) :: sys
        real(dp) :: energy
        real(dp) :: dx, dy, r
        integer  :: i, j

        energy = 0.0_dp

        ! Loop sobre todos los pares (i < j)
        ! El loop externo va de 1 a N-1, el interno de i+1 a N
        ! Esto evita contar cada par dos veces y el auto-término i=j
        do i = 1, sys%n - 1
            do j = i + 1, sys%n
                dx = sys%x(i) - sys%x(j)
                dy = sys%y(i) - sys%y(j)

                ! Distancia con softening para estabilidad numérica
                r = sqrt(dx*dx + dy*dy + EPSILON_SOFT*EPSILON_SOFT)

                ! Acumular contribución del par (i,j)
                energy = energy + K_COULOMB * sys%q(i) * sys%q(j) / r
            end do
        end do

    end function compute_total_energy

    !===========================================================================
    ! Función: compute_delta_energy
    !
    ! Calcula el CAMBIO en energía ΔU al mover la partícula idx
    ! desde su posición actual a (x_new, y_new).
    !
    ! Complejidad: O(N) — solo necesita evaluar interacciones de la
    ! partícula movida con todas las demás.
    !
    ! Algoritmo:
    !   ΔU = U_new_contribution(idx) - U_old_contribution(idx)
    !
    ! donde la contribución de la partícula idx es:
    !   U_contrib(idx) = k Σ(j≠idx) q_idx · q_j / |r_idx - r_j|
    !
    ! Si ΔU < 0, el movimiento reduce la energía → aceptar.
    ! Si ΔU ≥ 0, el movimiento aumenta la energía → rechazar.
    !
    ! Argumentos:
    !   sys   (in) — Estado actual del sistema
    !   idx   (in) — Índice de la partícula a mover (1..N)
    !   x_new (in) — Nueva coordenada x propuesta
    !   y_new (in) — Nueva coordenada y propuesta
    !===========================================================================
    function compute_delta_energy(sys, idx, x_new, y_new) result(delta_u)
        type(particle_system), intent(in) :: sys
        integer, intent(in)  :: idx
        real(dp), intent(in) :: x_new, y_new
        real(dp) :: delta_u

        real(dp) :: dx_old, dy_old, r_old
        real(dp) :: dx_new, dy_new, r_new
        real(dp) :: u_old, u_new
        integer  :: j

        u_old = 0.0_dp
        u_new = 0.0_dp

        ! Calcular contribución energética de partícula idx
        ! antes y después del movimiento propuesto
        do j = 1, sys%n
            if (j == idx) cycle  ! Saltar auto-interacción

            ! Distancia actual (antes del movimiento)
            dx_old = sys%x(idx) - sys%x(j)
            dy_old = sys%y(idx) - sys%y(j)
            r_old  = sqrt(dx_old*dx_old + dy_old*dy_old + EPSILON_SOFT*EPSILON_SOFT)

            ! Distancia propuesta (después del movimiento)
            dx_new = x_new - sys%x(j)
            dy_new = y_new - sys%y(j)
            r_new  = sqrt(dx_new*dx_new + dy_new*dy_new + EPSILON_SOFT*EPSILON_SOFT)

            ! Acumular contribuciones
            u_old = u_old + K_COULOMB * sys%q(idx) * sys%q(j) / r_old
            u_new = u_new + K_COULOMB * sys%q(idx) * sys%q(j) / r_new
        end do

        ! Cambio en energía total
        delta_u = u_new - u_old

    end function compute_delta_energy

    !===========================================================================
    ! Subrutina: compute_potential_at_point
    !
    ! Calcula el potencial eléctrico V(x,y) en un punto arbitrario
    ! debido a todas las cargas del sistema.
    !
    ! V(r) = k Σ_i q_i / |r - r_i|
    !
    ! Útil para generar mapas de calor del potencial.
    !===========================================================================
    function compute_potential(sys, xp, yp) result(potential)
        type(particle_system), intent(in) :: sys
        real(dp), intent(in) :: xp, yp
        real(dp) :: potential
        real(dp) :: dx, dy, r
        integer  :: i

        potential = 0.0_dp

        do i = 1, sys%n
            dx = xp - sys%x(i)
            dy = yp - sys%y(i)
            r  = sqrt(dx*dx + dy*dy + EPSILON_SOFT*EPSILON_SOFT)
            potential = potential + K_COULOMB * sys%q(i) / r
        end do

    end function compute_potential

end module mod_energy
