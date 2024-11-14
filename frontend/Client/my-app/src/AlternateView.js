import React, { useEffect, useState } from 'react';
import { ChakraProvider, Box, Image, Text, Button, HStack } from '@chakra-ui/react';
import alternateViewTheme from './theme'; // カスタムテーマのインポート

function AlternateView({ setIsAlternateView }) { // propsで関数を受け取る
    const [timeLeft, setTimeLeft] = useState(30); // 20秒のタイマー

    // タイマー処理: 1秒ごとに減少し、0で呼び出し画面に戻る
    useEffect(() => {
        if (timeLeft > 0) {
            const timer = setInterval(() => setTimeLeft((prev) => prev - 1), 1000);
            return () => clearInterval(timer); // クリーンアップ
        } else {
            // タイマーが0になったら呼び出し画面に戻る
            setIsAlternateView(false);
        }
    }, [timeLeft, setIsAlternateView]);

    return (
        <ChakraProvider theme={alternateViewTheme}>
            <Box
                height="100vh"
                width="100vw"
                display="flex"
                justifyContent="center"
                alignItems="center"
                overflow="hidden"
                position="relative"
                onClick={() => setIsAlternateView(false)} // クリックで呼び出し画面に戻る
            >
                <Image
                    src="/media/aa.png" // 画像のパスを修正 (public/media)
                    alt="説明画像"
                    objectFit="contain" // 画像全体を表示
                    height="100%"
                    width="100%"
                />

                {/* 左下にタイマーとボタンを表示 */}
                <HStack
                    position="absolute"
                    bottom="20px"
                    left="20px"
                    spacing={4}
                    align="center"
                >
                    {/* タイマー表示 */}
                    <Text fontSize="2xl" color="white" fontWeight="bold">
                        {timeLeft}
                    </Text>

                    {/* 呼び出し画面に戻るボタン */}
                    <Button
                        colorScheme="teal"
                        onClick={() => setIsAlternateView(false)} // 呼び出し画面に戻る
                    >
                        呼び出し画面に戻る
                    </Button>
                </HStack>
            </Box>
        </ChakraProvider>
    );
}

export default AlternateView;
