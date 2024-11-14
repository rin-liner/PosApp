// theme.js
import { extendTheme } from '@chakra-ui/react';

const alternateViewTheme = extendTheme({
    fonts: {
        heading: 'UDDigiKyokasho, sans-serif',  // ヘッディングに適用
        body: 'UDDigiKyokasho, sans-serif',  // テキストに適用
    },
    styles: {
        global: {
            '@font-face': {
                fontFamily: 'UDDigiKyokasho',
                src: 'url("/fonts/UDDigiKyokashoN-R.ttc") format("truetype")',
                fontWeight: 'normal',
                fontStyle: 'normal',
            },
        },
    },
});

export default alternateViewTheme;
