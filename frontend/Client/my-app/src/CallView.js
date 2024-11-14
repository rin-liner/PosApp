import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    ChakraProvider,
    Box,
    Heading,
    VStack,
    SimpleGrid,
    Text,
    Button,
    Center,
    Fade,
} from '@chakra-ui/react';
import axios from 'axios';
import { io } from 'socket.io-client';
import { SERVER_IP } from './App';
import { useNavigate } from 'react-router-dom';
import AlternateView from './AlternateView'; // AlternateViewのインポート

function CallView() {
    const [waitingOrders, setWaitingOrders] = useState([]);
    const [calledOrders, setCalledOrders] = useState([]);
    const [showNextPlease, setShowNextPlease] = useState(false);
    const [isAlternateView, setIsAlternateView] = useState(false); // 初回は呼び出し画面
    const socket = useRef();
    const navigate = useNavigate();
    const noCalledOrderTimeout = useRef(null);
    const intervalRef = useRef(null);

    // 20秒別画面、10秒呼び出し画面のサイクル開始
    const startAlternateViewCycle = useCallback(() => {
        intervalRef.current = setInterval(() => {
            setIsAlternateView((prev) => !prev); // 20秒/10秒で切り替え
        }, 30000); // 30秒周期: 20秒別画面 + 10秒呼び出し画面
    }, []);

    // 呼び出しがなくなった後の20秒タイマー開始
    const startNoCalledOrderTimeout = useCallback(() => {
        noCalledOrderTimeout.current = setTimeout(() => {
            setIsAlternateView(true); // 別画面に切り替え
            startAlternateViewCycle(); // サイクル開始
        }, 20000); // 20秒待機後に別画面へ切り替え
    }, [startAlternateViewCycle]);

    // 呼び出しが発生したときのタイマーリセット
    const resetNoCalledOrderTimeout = useCallback(() => {
        clearTimeout(noCalledOrderTimeout.current); // 現在のタイマーをリセット
        clearInterval(intervalRef.current); // サイクル停止
        setIsAlternateView(false); // 呼び出し画面に戻す
    }, []);

    // 初回ロード時の未完了注文の取得
    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const response = await axios.get(`http://${SERVER_IP}:5000/orders`);
                if (response.status === 200) {
                    const incompleteOrders = response.data.filter(order => !order.is_completed);
                    const waitingOrderIds = incompleteOrders.map(order => order.order_id);
                    setWaitingOrders(waitingOrderIds);
                }
            } catch (error) {
                console.error('注文データの取得中にエラーが発生しました:', error);
            }
        };
        fetchOrders();
    }, []);

    // 初回起動時に呼び出し画面を表示し、呼び出しがなければ20秒後に別画面へ
    useEffect(() => {
        startNoCalledOrderTimeout(); // 呼び出しがない場合のタイマー開始

        return () => {
            clearTimeout(noCalledOrderTimeout.current); // クリーンアップ
            clearInterval(intervalRef.current);
        };
    }, [startNoCalledOrderTimeout]);

    // Socket.IO の接続とイベントリスナーの設定
    useEffect(() => {
        socket.current = io(`http://${SERVER_IP}:5000`, {
            transports: ['websocket'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
        });

        socket.current.on('new_order', (orderData) => {
            setWaitingOrders((prevOrders) => [...prevOrders, orderData.order_id]);
        });

        socket.current.on('order_call', (orderData) => {
            setWaitingOrders((prevOrders) =>
                prevOrders.filter((orderId) => orderId !== orderData.order_id)
            );
            setCalledOrders((prevOrders) => {
                const updatedOrders = [...prevOrders, orderData.order_id];
                return updatedOrders.slice(-4); // 最大4件まで表示
            });
            resetNoCalledOrderTimeout(); // 呼び出しが発生した場合のタイマーリセット
        });

        socket.current.on('end_order', (orderData) => {
            setCalledOrders((prevOrders) =>
                prevOrders.filter((orderId) => orderId !== orderData.order_id)
            );
            if (calledOrders.length === 1) startNoCalledOrderTimeout(); // タイマー開始
        });

        return () => {
            socket.current.disconnect(); // クリーンアップ
        };
    }, [calledOrders, resetNoCalledOrderTimeout, startNoCalledOrderTimeout]);

    // 「Next Please」メッセージの5秒表示・10秒非表示のサイクル
    useEffect(() => {
        let showTimeout, hideTimeout;

        const toggleVisibility = () => {
            setShowNextPlease(true); // 5秒間表示
            showTimeout = setTimeout(() => {
                setShowNextPlease(false); // 10秒間非表示
                hideTimeout = setTimeout(toggleVisibility, 10000); // 次のサイクル開始
            }, 5000);
        };

        toggleVisibility(); // 初回開始

        return () => {
            clearTimeout(showTimeout);
            clearTimeout(hideTimeout); // クリーンアップ
        };
    }, []);

    // 別画面の表示状態
    if (isAlternateView) {
        return <AlternateView setIsAlternateView={setIsAlternateView} />; // 呼び出し画面への切り替え用関数を渡す
    }

    return (
        <ChakraProvider>
            <Box p={5} maxWidth="1200px" mx="auto">
                <Box position="absolute" top={0} right={0} m={4}>
                    <Button colorScheme="teal" onClick={() => navigate('/')}>
                        注文画面に移動
                    </Button>
                </Box>

                {/* Next Please メッセージ */}
                <Fade in={showNextPlease}>
                    <Center position="absolute" top={40} right={90} m={4}>
                        <Text fontSize="3xl" fontWeight="bold" color="teal.500">
                            Next Please!
                        </Text>
                    </Center>
                </Fade>

                <Heading as="h1" size="xl" textAlign="center" mb={5}>
                    呼び出し画面
                </Heading>
                <Heading as="h2" size="lg" textAlign="center" mb={5} color="gray.500">
                    お手元のレシート番号をご参照ください
                </Heading>
                <SimpleGrid columns={2} spacing={10}>
                    {/* 呼び出し待ち注文 */}
                    <Box borderWidth="1px" borderRadius="lg" p={4}>
                        <Heading as="h2" size="lg" mb={4} textAlign="center">
                            お待ち番号
                        </Heading>
                        <SimpleGrid columns={2} spacing={4}>
                            {waitingOrders.length > 0 ? (
                                waitingOrders.slice(0, 10).map((orderId, index) => (
                                    <Center key={index} p={4}>
                                        <Text fontSize="6xl" color="gray.600" fontWeight="bold">
                                            {orderId}
                                        </Text>
                                    </Center>
                                ))
                            ) : (
                                <Center p={4}>
                                    <Text fontSize="4xl" color="gray.400">
                                        No orders...
                                    </Text>
                                </Center>
                            )}
                        </SimpleGrid>
                    </Box>

                    {/* 呼び出し中注文 */}
                    <Box borderWidth="1px" borderRadius="lg" p={4}>
                        <Heading as="h2" size="lg" mb={4} textAlign="center">
                            お呼び出し中の番号
                        </Heading>
                        <VStack spacing={4} align="stretch">
                            {calledOrders.length > 0 ? (
                                calledOrders.map((orderId, index) => (
                                    <Center key={index} p={4}>
                                        <Text fontSize="8xl" color="green.500" fontWeight="extrabold">
                                            {orderId}
                                        </Text>
                                    </Center>
                                ))
                            ) : (
                                <Center p={4}>
                                    <Text fontSize="4xl" color="gray.400">
                                        No orders...
                                    </Text>
                                </Center>
                            )}
                        </VStack>
                    </Box>
                </SimpleGrid>
            </Box>
        </ChakraProvider>
    );
}

export default CallView;
