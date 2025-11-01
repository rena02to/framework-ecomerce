'use client';
import Link from "next/link";
import styles from "./style.module.css";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { toast } from "react-toastify";



interface Image{
  id: number;
  image: string;
}

interface Categorie{
  id: number;
  name: string;
}

interface Product {
  id: number;
  name: string;
  value: number;
  images: Image[];
  categories: Categorie[];
}

interface Return{
    product: Product;
    amount: number;
}


export default function Home() {
    const router = useRouter();
    const [products, setProducts]=useState<Return[]>([]);
    const [total, setTotal]=useState(0);

    const SendSale = async() => {
        try{
            const response = await fetch(`http://localhost:8000/api/orders/`,{
                credentials: 'include',
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ payment_method: 1 }),
            })
            
            if(response.ok){
                toast.success("Compra realizada com sucesso!");
            }
        }  catch(error){
            console.error(error);
        }
    }

    const UpdateItemCart = async(id: number, amount: number) => {
        try{
            const response = await fetch(`http://localhost:8000/api/carts/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product: id, amount: amount }),
            });
            
            if(response.ok){
                toast.success("Carrinho atualizado com sucesso!");
            }
        }  catch(error){
            console.error(error);
        }
    }

    useEffect(() => {
        const MeData = async() => {
            try{
                const response = await fetch(`http://localhost:8000/api/users/me/`,{
                    credentials: 'include'
                })
                
                if(!response.ok){
                    router.push('/login');
                }
            }  catch(error){
                console.error(error);
            }
        }

        const CartData = async() => {
            try{
                const response = await fetch(`http://localhost:8000/api/carts/`,{
                    credentials: 'include'
                })

                if (response.ok) {
                    const data = await response.json();
                    setProducts(data.data);
                    setTotal(data.total);
                }
            }  catch(error){
                console.error(error);
            }
        }

        MeData();
        CartData();
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
            <h1>Carrinho</h1>
            <div className={styles.productList}>
                {products.map((product, index) => (
                    <div className={styles.productCard} key={index}>
                        <div className={styles.top}>
                        <Image
                            src={product.product.images[0] ? `http://localhost:8000/${product.product.images[0].image}` : ''}
                            alt={product.product.name}
                            className={styles.productImage}
                            width={100}
                            height={100}
                        />
                        <h2 className={styles.productName}>{product.product.name}</h2>
                        <div className={styles.categories}>
                            {product.product.categories.map((category, index) => (
                            <span key={index} className={styles.category}>
                                {category.name}
                            </span>
                            ))}
                        </div>
                            <p className={styles.productPrice}>
                                <button onClick={()=>UpdateItemCart(product.product.id, -1)}>-</button>
                                <span>{product.amount}</span>
                                <button  onClick={()=>UpdateItemCart(product.product.id, 1)}>+</button>
                                <span>X</span>
                                <span>{product.product.value}</span>
                            </p>
                        </div>
                    </div>
                ))}
            </div>
            <div className={styles.total}>
                <button type="button" className={styles.finally} onClick={()=>SendSale()}>Pagar {total}</button>
            </div>
        </div>
    );
}
