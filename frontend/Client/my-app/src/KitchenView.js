import React, { useState, useEffect, useRef } from 'react';
import {
    ChakraProvider,
    Box,
    Heading,
    VStack,
    SimpleGrid,
    Button,
} from '@chakra-ui/react';
import axios from 'axios';
import { io } from 'socket.io-client';
import { SERVER_IP } from './App';
import { useNavigate } from 'react-router-dom';

function KitchenView() {
    const [orders, setOrders] = useState([]);
    const socket = useRef();
    const navigate = useNavigate();

    // 初回ロード時に未完了の注文を取得
    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const response = await axios.get(`http://${SERVER_IP}:5000/orders`);
                if (response.status === 200) {
                    setOrders(response.data);
                }
            } catch (error) {
                console.error('注文データの取得中にエラーが発生しました:', error);
            }
        };
        fetchOrders();
    }, []);

    // Socket.IO の接続とイベントリスナーの設定
    useEffect(() => {
        socket.current = io(`http://${SERVER_IP}:5000`, {
            transports: ['websocket'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
        });

        socket.current.on('connect', () => {
            console.log('Socket.IO に接続されました');
        });

        socket.current.on('connect_error', (err) => {
            console.error('Socket.IO 接続エラー:', err);
        });

        // 新しい注文が来たときの処理
        socket.current.on('new_order', (orderData) => {
            setOrders((prevOrders) => [...prevOrders, orderData]);
        });

        // 注文呼び出し時の処理
        socket.current.on('order_call', (data) => {
            setOrders((prevOrders) =>
                prevOrders.map((order) =>
                    order.order_id === data.order_id ? { ...order, isHighlighted: true } : order
                )
            );
        });

        // 注文終了時の処理
        socket.current.on('end_order', (data) => {
            setOrders((prevOrders) =>
                prevOrders.filter((order) => order.order_id !== data.order_id)
            );
        });

        return () => {
            socket.current.disconnect();
        };
    }, []);

    // 注文をクリックしたときの処理
    const handleOrderClick = async (orderIndex) => {
        const updatedOrders = [...orders];
        const clickedOrder = updatedOrders[orderIndex];

        clickedOrder.isHighlighted = !clickedOrder.isHighlighted;
        setOrders(updatedOrders);

        if (clickedOrder.isHighlighted) {
            try {
                socket.current.emit('order_call', { order_id: clickedOrder.order_id });
                const text = `${clickedOrder.order_id}番のお客様、商品が出来上がったのだ!`;
                await axios.post(`http://${SERVER_IP}:5000/order_call`, {
                    order_id: clickedOrder.order_id,
                    text,
                });
            } catch (error) {
                console.error('注文呼び出し中にエラーが発生しました:', error);
                alert('注文呼び出しに失敗しました。再試行してください。');
            }
        } else {
            socket.current.emit('end_order', { order_id: clickedOrder.order_id });
        }
    };

    return (
        <ChakraProvider>
            <Box p={5} maxWidth="1200px" mx="auto" position="relative">
                <Box position="absolute" top={0} right={0} m={4}>
                    <Button colorScheme="teal" onClick={() => navigate('/')}>
                        注文画面に移動
                    </Button>
                </Box>
                <Heading as="h1" size="xl" textAlign="center">
                    厨房画面
                </Heading>
                <SimpleGrid columns={2} spacing={10} mt={5}>
                    {orders.slice(0, 4).map((order, index) => (
                        <Box
                            key={order.order_id}
                            borderWidth="1px"
                            borderRadius="lg"
                            p={4}
                            bg={order.isHighlighted ? 'yellow.200' : 'white'}
                            onClick={() => handleOrderClick(index)}
                            cursor="pointer"
                        >
                            <Heading
                                as="h3"
                                size="lg"
                                textAlign="center"
                                color={order.isHighlighted ? 'black' : 'inherit'}
                            >
                                注文ID: {order.order_id}
                            </Heading>

                            {/* 商品リスト */}
                            <VStack align="start" mt={3} spacing={2}>
                                {order.menuL.map((item, itemIndex) => (
                                    <Box key={itemIndex} fontSize="2xl" fontWeight="bold">
                                        {item.name} × {item.quantity}
                                    </Box>
                                ))}
                            </VStack>

                            {/* メモ */}
                            <Box mt={4} textAlign="center" fontSize="2xl" fontWeight="bold">
                                メモ: {order.note || 'なし'}
                            </Box>
                        </Box>
                    ))}
                </SimpleGrid>
                {orders.length > 4 && (
                    <Box mt={5} textAlign="right" fontWeight="bold" color="gray.600">
                        more {orders.length - 4} order(s)
                    </Box>
                )}
            </Box>
        </ChakraProvider>
    );
}

export default KitchenView;
