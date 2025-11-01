'use client';
import Link from "next/link";
import styles from "./style.module.css";
import { useEffect, useState } from "react";
import Image from "next/image";
import { toast } from "react-toastify";
import { useRouter } from "next/navigation";


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


export default function HomeComponent() {
  const router = useRouter();
  const [products, setProducts] = useState([]);
  
  const addCart = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/carts/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ product: id, amount: 1 }),
      });
        
      if (response.ok) {
        toast.success('Produto adicionado ao carrinho com sucesso!');
      }else{
        router.push('/login');
      }
    } catch (error) {
      console.error(error);
    }
  };

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

    const getRecommendations = async() => {
      try{
        const response = await fetch(`http://localhost:8000/api/recommendations/last_purchase/`,{
          credentials: 'include'
        })

        if(response.ok){
          const data = await response.json();
          setProducts(data.products);
        }
      }  catch(error){
        console.error(error);
      }
    }

    MeData();
    getRecommendations();
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
      <main className={styles.main}>
        <h1>Recomendações de produtos</h1>
        <div className={styles.productList}>
          {products.map((product: Product) => (
            <div className={styles.productCard} key={product.id}>
                <div className={styles.top}>
                  <Image
                    src={product.images[0] ? `http://localhost:8000/${product.images[0].image}` : ''}
                    alt={product.name}
                    className={styles.productImage}
                    width={100}
                    height={100}
                    />
                  <h2 className={styles.productName}>{product.name}</h2>
                  <div className={styles.categories}>
                    {product.categories.map((category, index) => (
                      <span key={index} className={styles.category}>
                        {category.name}
                      </span>
                    ))}
                  </div>
                  <p className={styles.productPrice}>{product.value}</p>
                </div>
                <button type="button" className={styles.addCart} onClick={()=>addCart(product.id)}>Adicionar ao carrinho</button>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
