import React, { useEffect, useState } from 'react';
import {
  ChakraProvider,
  Box,
  Heading,
  VStack,
  Button,
  SimpleGrid,
  Input,
  Grid,
  Checkbox,
  useToast,
  HStack,
  Textarea,
  Text,
} from '@chakra-ui/react';
import axios from 'axios';
import { BrowserRouter as Router, Route, Routes, useNavigate, Link } from 'react-router-dom';
import KitchenView from './KitchenView';
import CallView from './CallView';

const hostname = window.location.hostname;

export let SERVER_IP;
if (hostname === "localhost") {
  SERVER_IP = "localhost";
} else if (hostname === "192.168.10.101") {
  SERVER_IP = "192.168.10.101";
} else if (hostname === "192.168.10.102") {
  SERVER_IP = "192.168.10.102";
} else {
  SERVER_IP = "localhost"; // デフォルトのIP
}


// 商品管理画面のコンポーネント
function ProductManagement() {
  const [products, setProducts] = useState([]);
  const [newProductName, setNewProductName] = useState('');
  const [newProductPrice, setNewProductPrice] = useState(0);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`http://${SERVER_IP}:5000/products`)
      .then((response) => {
        setProducts(response.data);
      })
      .catch((error) => {
        console.error('商品リストの取得中にエラーが発生しました:', error);
        toast({
          title: '商品リストの取得に失敗しました',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  }, [toast]);

  // 商品の追加処理
  const handleAddProduct = () => {
    const newProduct = {
      name: newProductName,
      price: newProductPrice,
      onSale: true,
      category: 'menu',
      description: '', // 必要に応じて説明を追加
    };

    axios.post(`http://${SERVER_IP}:5000/product_management`, newProduct)
      .then((response) => {
        if (response.status === 201) {
          setProducts([...products, response.data]);
          setNewProductName('');
          setNewProductPrice(0);
          toast({
            title: '商品が追加されました',
            status: 'success',
            duration: 2000,
            isClosable: true,
          });
        }
      })
      .catch((error) => {
        console.error('商品追加中にエラーが発生しました:', error);
        toast({
          title: '商品追加に失敗しました',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  };

  // 商品の削除処理
  const handleDeleteProduct = (productId) => {
    const confirmDelete = window.confirm("本当にこの商品を削除しますか？");
    if (!confirmDelete) {
      return;
    }

    axios.delete(`http://${SERVER_IP}:5000/product_management/${productId}`)
      .then(() => {
        setProducts(products.filter(product => product.product_id !== productId));
        toast({
          title: '商品が削除されました',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
      })
      .catch((error) => {
        console.error('商品削除中にエラーが発生しました:', error);
        toast({
          title: '商品削除に失敗しました',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  };

  // 販売 on/off 切り替え
  const handleToggleSale = (productId) => {
    const updatedProducts = products.map((product) => {
      if (product.product_id === productId) {
        return { ...product, onSale: !product.onSale };
      }
      return product;
    });
    setProducts(updatedProducts);
  };

  // 価格変更処理
  const handleChangePrice = (productId, amount) => {
    const updatedProducts = products.map((product) => {
      if (product.product_id === productId) {
        const updatedPrice = product.price + amount;
        return { ...product, price: updatedPrice > 0 ? updatedPrice : 0 };
      }
      return product;
    });
    setProducts(updatedProducts);
  };

  // 保存処理
  const handleSaveChanges = (productId) => {
    const updatedProduct = products.find((product) => product.product_id === productId);
    axios.put(`http://${SERVER_IP}:5000/product_management/${productId}`, updatedProduct)
      .then(() => {
        toast({
          title: '変更が保存されました',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
      })
      .catch((error) => {
        console.error('変更の保存中にエラーが発生しました:', error);
        toast({
          title: '変更の保存に失敗しました',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  };

  return (
    <ChakraProvider>
      <Box p={5} maxWidth="1200px" mx="auto" position="relative">
        {/* 注文画面に戻るボタンを画面左上に配置 */}
        <Box position="absolute" top={0} left={0} m={4}>
          <Button colorScheme="blue" onClick={() => navigate('/')}>注文画面に戻る</Button>
        </Box>

        <Heading as="h1" size="xl" textAlign="center">
          商品管理画面
        </Heading>

        <HStack align="start" spacing={10} mt={5}>
          {/* 商品リストを画面左 3/4 に配置 */}
          <Box flex="3">
            <VStack spacing={5} align="stretch">
              {products.map((product) => (
                <Box key={product.product_id} borderWidth="1px" borderRadius="lg" p={4}>
                  <HStack justifyContent="space-between">
                    <Box>
                      <Heading as="h3" size="md">{product.name}</Heading>
                      <p>価格: ¥{product.price.toLocaleString()}</p>
                    </Box>
                    <VStack>
                      <Button size="sm" colorScheme="red" onClick={() => handleDeleteProduct(product.product_id)}>
                        削除
                      </Button>
                      <Checkbox
                        isChecked={product.onSale}
                        onChange={() => handleToggleSale(product.product_id)}
                      >
                        販売中
                      </Checkbox>
                      <HStack>
                        <Button size="sm" onClick={() => handleChangePrice(product.product_id, 10)}>+10円</Button>
                        <Button size="sm" onClick={() => handleChangePrice(product.product_id, -10)}>-10円</Button>
                      </HStack>
                      <Button size="sm" colorScheme="blue" onClick={() => handleSaveChanges(product.product_id)}>
                        設定を保存
                      </Button>
                    </VStack>
                  </HStack>
                </Box>
              ))}
            </VStack>
          </Box>

          {/* 新規商品追加フォームを画面右 1/4 に配置 */}
          <Box flex="1">
            <Heading as="h2" size="lg">新規商品追加</Heading>
            <VStack mt={3} spacing={3}>
              <Input
                placeholder="商品名"
                value={newProductName}
                onChange={(e) => setNewProductName(e.target.value)}
              />
              <Input
                placeholder="価格"
                type="number"
                value={newProductPrice}
                onChange={(e) => setNewProductPrice(parseInt(e.target.value))}
              />
              <Button colorScheme="teal" onClick={handleAddProduct}>商品を追加</Button>
            </VStack>
          </Box>
        </HStack>

        {/* 注文履歴画面に移動するリンク */}
        <VStack mt={5} spacing={3}>
          <Link to="/order-history">
            <Button colorScheme="teal" size="lg">
              注文履歴画面に移動
            </Button>
          </Link>
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

// 注文履歴画面のコンポーネント
function OrderHistory() {
  const [orderHistory, setOrderHistory] = useState([]);
  const [totalItemsSold, setTotalItemsSold] = useState(0);
  const [totalSalesAmount, setTotalSalesAmount] = useState(0);
  const toast = useToast();
  const navigate = useNavigate();

  // 注文履歴の取得
  useEffect(() => {
    axios.get(`http://${SERVER_IP}:5000/order_history`)
      .then((response) => {
        setOrderHistory(response.data.order_history);
        setTotalItemsSold(response.data.total_items_sold);  // 合計商品の個数をセット
        setTotalSalesAmount(response.data.total_sales_amount);  // 合計販売額をセット
      })
      .catch((error) => {
        console.error('注文履歴の取得中にエラーが発生しました:', error);
        toast({
          title: '注文履歴の取得に失敗しました',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  }, [toast]);

  return (
    <ChakraProvider>
      <Box p={5} maxWidth="1200px" mx="auto">
        <Box position="absolute" top={0} left={300} m={4}>
          <Button colorScheme="blue" onClick={() => navigate('/product-management')}>
            商品管理画面に戻る
          </Button>
        </Box>
        <Heading as="h1" size="xl" textAlign="center">
          注文履歴
        </Heading>
        <VStack spacing={5} align="stretch" mt={5}>
          {orderHistory.map((order) => (
            <Box key={order.order_id} borderWidth="1px" borderRadius="lg" p={4}>
              <Heading as="h3" size="md">
                注文ID: {order.order_id}
              </Heading>
              <Text>日時: {new Date(order.created_at).toLocaleString('ja-JP', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false,
                timeZone: 'Asia/Tokyo'
              })}
              </Text>
              <Text>メモ: {order.note || 'なし'}</Text>

              <Box mt={3}>
                <Heading as="h4" size="sm">
                  商品一覧:
                </Heading>
                {order.products.map((product, index) => (
                  <HStack key={index} justifyContent="space-between" mt={2}>
                    <Text>
                      {product.name} @ ¥{product.unit_price} × {product.quantity}
                    </Text>
                    <Text>¥{product.total_price.toLocaleString()}</Text>
                  </HStack>
                ))}
              </Box>

              <HStack justifyContent="flex-end" mt={4}>
                <Text fontWeight="bold">合計金額: ¥{order.total_price.toLocaleString()}</Text>
              </HStack>
            </Box>
          ))}
        </VStack>

        {/* 合計商品数と合計販売額を表示 */}
        <Box mt={10} borderWidth="1px" borderRadius="lg" p={4}>
          <HStack justifyContent="space-between">
            <Text fontSize="xl" fontWeight="bold">合計商品数:</Text>
            <Text fontSize="xl">{totalItemsSold}</Text>
          </HStack>
          <HStack justifyContent="space-between" mt={4}>
            <Text fontSize="xl" fontWeight="bold">合計販売額:</Text>
            <Text fontSize="xl">¥{totalSalesAmount.toLocaleString()}</Text>
          </HStack>
        </Box>

        <Box mt={10}>
          <Button colorScheme="blue" onClick={() => navigate('/product-management')}>
            商品管理画面に戻る
          </Button>
        </Box>
      </Box>
    </ChakraProvider>
  );
}


// Appコンポーネント
function App() {
  const toast = useToast();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [orderItems, setOrderItems] = useState([]);
  const [note, setNote] = useState('');

  // 商品リストの取得
  useEffect(() => {
    axios
      .get(`http://${SERVER_IP}:5000/products`)
      .then((response) => {
        setProducts(response.data);
      })
      .catch((error) => {
        console.error('商品リストの取得中にエラーが発生しました:', error);
        toast({
          title: '商品リストの取得に失敗しました',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  }, [toast]);

  // 商品追加処理
  const handleAddToOrder = (product) => {
    const existingItemIndex = orderItems.findIndex(
      (item) => item.product_id === product.product_id
    );
    if (existingItemIndex >= 0) {
      const updatedItems = [...orderItems];
      updatedItems[existingItemIndex].quantity += 1;
      setOrderItems(updatedItems);
    } else {
      setOrderItems([...orderItems, { ...product, quantity: 1 }]);
    }
  };

  // 商品削除処理
  const handleRemoveFromOrder = (productId) => {
    setOrderItems(orderItems.filter((item) => item.product_id !== productId));
  };

  // 数量増減処理
  const handleChangeQuantity = (productId, amount) => {
    const updatedItems = orderItems.map((item) =>
      item.product_id === productId
        ? { ...item, quantity: Math.max(item.quantity + amount, 1) }
        : item
    );
    setOrderItems(updatedItems);
  };

  // 注文確定処理
  const handleConfirmOrder = () => {
    if (orderItems.length === 0) {
      toast({
        title: '注文が空です',
        status: 'warning',
        duration: 2000,
        isClosable: true,
      });
      return;
    }

    const orderData = {
      orderL: orderItems.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
      totalL: orderItems.map((item) => item.price * item.quantity),
      total: orderItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
      ),
      payment: 0,
      note: note || null,
      menuL: orderItems.map((item) => ({
        name: item.name,
        price: item.price,
        quantity: item.quantity,
      })),
    };

    axios
      .post(`http://${SERVER_IP}:5000/order`, orderData, { withCredentials: true })
      .then((response) => {
        if (response.status === 200) {
          const redirectUrl = response.data.redirect_url;
          navigate(redirectUrl);
        }
      })
      .catch((error) => {
        console.error('注文確定中にエラーが発生しました:', error);
        toast({
          title: '注文確定に失敗しました',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  };

  return (
    <ChakraProvider>
      <Box p={5} maxWidth="1200px" mx="auto" position="relative">
        {/* 厨房画面と呼び出し画面へのボタン */}
        <Box position="absolute" top={0} right={0} m={4}>
          <VStack spacing={4} align="stretch">
            <Button colorScheme="teal" onClick={() => navigate('/Kitchen')}>
              厨房画面に移動
            </Button>
            <Button colorScheme="teal" onClick={() => navigate('/Call')}>
              呼び出し画面に移動
            </Button>
          </VStack>
        </Box>

        <VStack spacing={5} align="stretch">
          <Heading as="h1" size="xl" textAlign="center">
            注文画面
          </Heading>
          <SimpleGrid columns={2} spacing={10}>
            {/* 商品リスト */}
            <Box>
              <Heading as="h2" size="lg" mb={4}>
                商品リスト
              </Heading>
              {products.map((product) => (
                <Button
                  key={product.product_id}
                  colorScheme={product.onSale ? 'teal' : 'gray'}
                  size="lg"
                  mb={2}
                  onClick={() => handleAddToOrder(product)}
                  isDisabled={!product.onSale}
                >
                  {product.name} ¥{product.price}
                </Button>
              ))}
            </Box>

            {/* 注文リスト */}
            <Box>
              <Heading as="h2" size="lg" mb={4}>
                注文リスト
              </Heading>
              <VStack spacing={2} align="stretch">
                {orderItems.map((item, index) => (
                  <Box key={index} borderWidth="1px" borderRadius="lg" p={4}>
                    {item.name} - ¥{item.price} × {item.quantity}
                    <HStack spacing={2} mt={2}>
                      <Button
                        size="xs"
                        colorScheme="red"
                        onClick={() => handleRemoveFromOrder(item.product_id)}
                      >
                        削除
                      </Button>
                      <Button
                        size="xs"
                        onClick={() => handleChangeQuantity(item.product_id, -1)}
                      >
                        -
                      </Button>
                      <Button
                        size="xs"
                        onClick={() => handleChangeQuantity(item.product_id, 1)}
                      >
                        +
                      </Button>
                    </HStack>
                  </Box>
                ))}
                <Textarea
                  placeholder="noteの入力"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                />
                <Button size="lg" colorScheme="blue" mt={4} onClick={handleConfirmOrder}>
                  注文確定
                </Button>
              </VStack>
            </Box>
          </SimpleGrid>

          {/* 商品管理画面へのリンク */}
          <Box mt={10}>
            <Link to="/product-management">
              <Button colorScheme="teal" size="lg">
                商品管理画面に移動
              </Button>
            </Link>
          </Box>
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

// PayPage コンポーネント
function PayPage() {
  const [payment, setPayment] = useState('');
  const [orderData, setOrderData] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`http://${SERVER_IP}:5000/current_order`, { withCredentials: true })
      .then((response) => {
        if (response.status === 200) {
          setOrderData(response.data);
        }
      })
      .catch((error) => {
        console.error('注文データの取得中にエラーが発生しました:', error);
        toast({
          title: '注文データの取得に失敗しました',
          status: 'error',
          duration: 2000,
          isClosable: true,
        });
      });
  }, [toast]);

  const addNumber = (num) => {
    setPayment((prev) => prev + num);
  };

  const addDirectAmount = (amount) => {
    setPayment(amount.toString());
    if (amount >= orderData.total) {
      handleConfirmPayment(amount);
    } else {
      toast({
        title: '支払い金額が不足しています',
        status: 'warning',
        duration: 2000,
        isClosable: true,
      });
    }
  };

  const clearInput = () => {
    setPayment('');
  };

  const deleteNumber = () => {
    setPayment((prev) => prev.slice(0, -1));
  };

  const handleConfirmPayment = (inputPayment = parseInt(payment)) => {
    if (inputPayment >= orderData.total) {
      setIsProcessing(true);

      toast({
        title: '注文完了！レシート印刷中…',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      axios.post(`http://${SERVER_IP}:5000/pay`, { payment: inputPayment }, { withCredentials: true })
        .then(() => {
          setPayment('');
          navigate('/');
        })
        .catch((error) => {
          console.error('支払い処理中にエラーが発生しました:', error);
          toast({
            title: '支払いに失敗しました',
            status: 'error',
            duration: 2000,
            isClosable: true,
          });
          setIsProcessing(false);
        });
    } else {
      toast({
        title: '支払い金額が不足しています',
        status: 'warning',
        duration: 2000,
        isClosable: true,
      });
    }
  };

  const changeAmount = parseInt(payment || 0) - orderData.total;

  return (
    <ChakraProvider>
      <Box p={5} maxWidth="1200px" mx="auto">
        <Box mb={4} position="absolute" top={0} left={0} m={4}>
          <Button colorScheme="blue" onClick={() => navigate('/')}>注文画面に戻る</Button>
        </Box>

        <Heading as="h1" size="xl" mb={5} textAlign="center">支払い画面</Heading>
        <SimpleGrid columns={2} spacing={10}>
          {/* 左側: 注文内容、おつり */}
          <Box>
            <Heading as="h2" size="lg" mb={4}>注文内容</Heading>
            <VStack spacing={2} align="stretch" mb={4}>
              {orderData.menuL && orderData.menuL.map((item, index) => (
                <Box key={index} borderWidth="1px" borderRadius="lg" p={4}>
                  {item.name} - ¥{item.price} × {item.quantity || 1}
                </Box>
              ))}
            </VStack>

            {/* メモ (note) の表示 */}
            <Box mb={4}>
              <Heading as="h3" size="md" mb={2}>メモ:</Heading>
              <Text fontSize="lg">{orderData.note || 'なし'}</Text>
            </Box>

            <Heading as="h3" size="md" mb={2}>合計金額: ¥{parseInt(orderData.total || 0).toLocaleString()}</Heading>
            <Box mt={4}>
              <Heading as="h3" size="md">おつり:</Heading>
              <Text fontSize="lg" fontWeight="bold" color={changeAmount < 0 ? 'red.500' : 'black'}>
                ¥{changeAmount.toLocaleString()}
              </Text>
            </Box>
            <Button
              colorScheme="blue"
              mt={4}
              width="100%"
              height="60px"
              fontSize="2xl"
              onClick={() => handleConfirmPayment()}
              isDisabled={parseInt(payment) < orderData.total || isProcessing}
            >
              注文確定
            </Button>
          </Box>

          {/* 右側: テンキー、金額入力ボタン */}
          <Box>
            <Heading as="h2" size="lg" mb={4}>受取金額</Heading>
            <Input value={parseInt(payment || 0).toLocaleString()} readOnly mb={4} fontSize="2xl" height="60px" />

            <Grid templateColumns="repeat(3, 1fr)" gap={4} maxWidth="400px" mx="auto" mb={4}>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 'C', 0, '00', '←'].map((val, index) => (
                <Button
                  key={index}
                  height="80px"
                  fontSize="2xl"
                  onClick={() => {
                    if (val === 'C') clearInput();
                    else if (val === '←') deleteNumber();
                    else addNumber(val);
                  }}
                  isDisabled={isProcessing}
                >
                  {val}
                </Button>
              ))}
            </Grid>

            <Grid templateColumns="repeat(3, 1fr)" gap={4} maxWidth="400px" mx="auto" mb={4}>
              {[500, 1000, 'ちょうど'].map((amount) => (
                <Button
                  key={amount}
                  colorScheme="teal"
                  height="80px"
                  fontSize="2xl"
                  onClick={() =>
                    amount === 'ちょうど'
                      ? addDirectAmount(orderData.total) // 合計金額で支払い処理を行う
                      : addDirectAmount(amount)
                  }
                  isDisabled={isProcessing}
                >
                  {amount === 'ちょうど' ? amount : `¥${amount.toLocaleString()}`}
                </Button>
              ))}
            </Grid>
          </Box>
        </SimpleGrid>
      </Box>
    </ChakraProvider>
  );
}

// AppWrapper コンポーネント
export default function AppWrapper() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/pay" element={<PayPage />} />
        <Route path="/product-management" element={<ProductManagement />} />
        <Route path="/order-history" element={<OrderHistory />} />
        <Route path="/kitchen" element={<KitchenView />} />
        <Route path="/call" element={<CallView />} />
      </Routes>
    </Router>
  );
}
