import Swal from 'sweetalert2'

export const useAlert = () => {
    const success = (title: string, text: string = '') => {
        return Swal.fire({
            icon: 'success',
            title,
            text,
            timer: 3000,
            timerProgressBar: true,
            showConfirmButton: false,
            background: '#ffffff',
            color: '#020617',
            iconColor: '#0f172a',
            customClass: {
                popup: 'rounded-3xl border border-slate-100 shadow-2xl',
                title: 'text-xl font-bold tracking-tight',
            }
        })
    }

    const error = (title: string, text: string = '') => {
        return Swal.fire({
            icon: 'error',
            title,
            text,
            background: '#ffffff',
            color: '#020617',
            confirmButtonColor: '#0f172a',
            customClass: {
                popup: 'rounded-3xl border border-slate-100 shadow-2xl',
                title: 'text-xl font-bold tracking-tight',
                confirmButton: 'rounded-xl px-6 py-2.5 font-bold uppercase text-xs tracking-widest'
            }
        })
    }

    const confirm = (title: string, text: string = '', confirmButtonText: string = 'Confirm') => {
        return Swal.fire({
            title,
            text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#0f172a',
            cancelButtonColor: '#f1f5f9',
            confirmButtonText,
            cancelButtonText: 'Cancel',
            background: '#ffffff',
            color: '#020617',
            customClass: {
                popup: 'rounded-3xl border border-slate-100 shadow-2xl',
                title: 'text-xl font-bold tracking-tight',
                confirmButton: 'rounded-xl px-6 py-2.5 font-bold uppercase text-xs tracking-widest',
                cancelButton: 'rounded-xl px-6 py-2.5 font-bold uppercase text-xs tracking-widest text-slate-400'
            }
        })
    }

    const toast = (title: string, icon: 'success' | 'error' | 'warning' | 'info' = 'success') => {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            background: '#ffffff',
            color: '#020617',
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        })

        return Toast.fire({
            icon,
            title
        })
    }

    return {
        success,
        error,
        confirm,
        toast
    }
}
