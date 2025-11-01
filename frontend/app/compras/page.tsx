'use client';
import Link from "next/link";
import styles from "./style.module.css";
import { useEffect, useState } from "react"; 
import { useRouter } from "next/navigation";
import Image from "next/image";


interface Categorie{
  id: number;
  name: string;
}

interface Product {
  id: number;
  name: string;
  value: number;
  image: string;
  categories: Categorie[];
}

interface Order{
    payment_method: string;
    value: string;
    delivery_value: number; 
    timestamp: string;
    products: Product[];
}


export default function Home() {
    const router = useRouter();
    const [orders, setOrders]= useState<Order[]>([]); 

    
    useEffect(() => {
        const fetchData = async () => {
            
            try {
                const meResponse = await fetch(`http://localhost:8000/api/users/me/`, {
                    credentials: 'include'
                });

                if (!meResponse.ok) {
                    router.push('/login');
                    return; 
                }
            } catch (error) {
                console.error(error);
            }

            try {
                const ordersResponse = await fetch(`http://localhost:8000/api/orders/`, {
                    credentials: 'include'
                });

                if (ordersResponse.ok) {
                    const data = await ordersResponse.json();
                    setOrders(data.data); 
                } else {
                    console.error("Falha ao buscar pedidos.");
                }
            } catch (error) {
                console.error("Erro ao buscar pedidos:", error);
            }
        };

        fetchData();
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
            
            <div className={styles.content}>
                <h1>Minhas Compras</h1>

                {/* --- Mapeamento dos Pedidos --- */}
                <div className={styles.purchases}>
                    {orders.length === 0 ? (
                        <p>Você ainda não fez nenhuma compra.</p>
                    ) : (
                        // Mapeia cada pedido
                        orders.map((order) => (
                            <div key={order.timestamp} className={styles.orderCard}>
                                <h3>Pedido de {order.timestamp}</h3>
                                <p><strong>Valor Total:</strong> R$ {order.value}</p>
                                <p><strong>Forma de Pagamento:</strong> {order.payment_method}</p>
                                
                                <h4>Produtos neste Pedido:</h4>
                                <ul className={styles.productList}>
                                    {/* Mapeia os produtos dentro de cada pedido */}
                                    {order.products.map((product, index) => (
                                        <li className={styles.productItem} key={index}>
                                            <Image 
                                                src={`http://localhost:8000${product.image}`} // Pega a primeira imagem
                                                alt={product.name}
                                                className={styles.productImage}
                                                width={100}
                                                height={100}
                                            />
                                            <div className={styles.productInfo}>
                                                <strong>{product.name}</strong>
                                                <p>Valor: R$ {product.value}</p>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}