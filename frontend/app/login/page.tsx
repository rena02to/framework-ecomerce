'use client';
import Link from "next/link";
import styles from "./style.module.css";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";

export default function Home() {
    const router = useRouter();

    const login = async() => {
        const email = (document.getElementById('email') as HTMLInputElement).value;
        const password = (document.getElementById('password') as HTMLInputElement).value;
        try{
            const response = await fetch(`http://localhost:8000/api/users/login/`,{
                method: 'POST', 
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({email, password}),
            })

            if(response.ok){
                router.push('/');
            }else{
                toast.error('Erro ao logar. Verifique suas credenciais.');
            }
        }  catch(error){
            console.error(error);
        }
    }

    useEffect(() => {
        const MeData = async() => {
            try{
                const response = await fetch(`http://localhost:8000/api/users/me/`,{
                    credentials: "include",
                })

                if(response.ok){
                    router.push('/');
                }
            }  catch(error){
                console.error(error);
            }
        }

        MeData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <div className={styles.page}>
            <header className={styles.header}>
                <p className={styles.title}>CompraFacil</p>
                <Link href="/login">Login</Link>
                <Link href="/">Home</Link>
                <Link href="/recomendacao">Recomendações</Link>
                <Link href="/carrinho">Carrinho</Link>
                <Link href="/compras">Compras</Link>
            </header>
            <div className={styles.form}>
                <p>Login</p>
                <input type="email" name="email" id="email" />
                <input type="password" name="password" id="password" />
                <button type="submit" onClick={()=>login()}>Logar</button>
            </div>
        </div>
    );
}
