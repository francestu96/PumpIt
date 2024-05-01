import input from "input";
import { Web3 } from "web3";
import * as dotenv from "dotenv";
import { toWei } from "web3-utils";
import { TelegramClient } from "telegram";
import { NewMessage } from "telegram/events/index.js";
import { StringSession } from "telegram/sessions/index.js";
import * as routerABI from "./ABIs/routerABI.json" assert { type: "json" };
import * as tokenABI from "./ABIs/tokenABI.json" assert { type: "json" };

dotenv.config()
const web3 = new Web3(process.env.ALCHEMY_ENDPOINT);
const wallet = web3.eth.accounts.privateKeyToAccount(process.env.PRIV_KEY);
const routerContract = new web3.eth.Contract(routerABI.default, process.env.ROUTER_ADDRESS, { from: wallet.address });
const stringBuyAmount = toWei(process.env.AMOUNT, "ether");
const client = new TelegramClient(new StringSession(process.env.TELEGRAM_SESSION), parseInt(process.env.TELEGRAM_API_ID), process.env.TELEGRAM_API_HASH, { connectionRetries: 5 });

await client.start();

const getBnbOut = async (wbnbAddr, tokenAddr, amount) => {
    const outs = await routerContract.methods.getAmountsOut(amount, [tokenAddr, wbnbAddr]).call();
    return BigInt(outs[1]);
};

const swapTx = async (tokenA, tokenB, amountOutMin, weiAmount, isBuy) => {
    const data = isBuy
        ? routerContract.methods.swapExactETHForTokens(
            web3.utils.toHex(amountOutMin),
            [tokenA, tokenB],
            wallet.address,
            web3.utils.toHex(Math.round(Date.now()/1000)+60*20),
        )
        : routerContract.methods.swapExactTokensForETH(
            weiAmount,
            web3.utils.toHex(amountOutMin),
            [tokenA, tokenB],
            wallet.address,
            web3.utils.toHex(Math.round(Date.now()/1000)+60*20),
        );

    const estimatedGas = (await data.estimateGas({ from: wallet.address, value: isBuy ? weiAmount : 0 })) + BigInt(20000);
    const gasPrice = await web3.eth.getGasPrice();

    const count = await web3.eth.getTransactionCount(wallet.address);
    const rawTransaction = {
        "from": wallet.address,
        "gasPrice": web3.utils.toHex(gasPrice),
        "gas": web3.utils.toHex(estimatedGas),
        "to": process.env.ROUTER_ADDRESS,
        "value": isBuy ? web3.utils.toHex(BigInt(weiAmount)) : 0,
        "data": data.encodeABI(),
        "nonce": web3.utils.toHex(count)
    };

    const signedTxn = await web3.eth.accounts.signTransaction(rawTransaction, wallet.privateKey);
    const result = await web3.eth.sendSignedTransaction(signedTxn.rawTransaction);
    const tokens = BigInt(result.logs.filter(x => x.topics[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef")?.pop()?.data || 0, 16)
    return { hash: result.transactionHash, tokens };
}

const approveTx = async (tokenAddr, amountToApprove) => {
    const tokenContract = new web3.eth.Contract(tokenABI.default, tokenAddr, { from: wallet.address });
    const data = tokenContract.methods.approve(
        process.env.ROUTER_ADDRESS,
        amountToApprove
    );

    const estimatedGas = Number((await data.estimateGas({ from: wallet.address }))) + 20000;
    const gasPrice = await web3.eth.getGasPrice();

    const count = await web3.eth.getTransactionCount(wallet.address);
    const rawTransaction = {
        "from": wallet.address,
        "gasPrice": web3.utils.toHex(gasPrice),
        "gas": web3.utils.toHex(estimatedGas),
        "to": tokenAddr,
        "data": data.encodeABI(),
        "nonce": web3.utils.toHex(count)
    };

    const signedTxn = await web3.eth.accounts.signTransaction(rawTransaction, wallet.privateKey);
    const result = await web3.eth.sendSignedTransaction(signedTxn.rawTransaction);
    return result;
}

const msgHandler = async (event) => {
    console.log(`${new Date().toLocaleString()}: ${event.message.message || event}\n`);
    // const tokenAddr = event.message.message.match(/^0x[a-fA-F0-9]{40}$/m);

    // if (tokenAddr?.length == 1) {
    //     try {
    //         const buyTx = await swapTx(process.env.WBNB_ADDRESS, tokenAddr[0], 0, stringBuyAmount, true);
    //         console.log(`✅ Successfully bought ${buyTx.tokens} tokens at tx hash: ${buyTx.hash}`);
    //         await approveTx(tokenAddr[0], buyTx.tokens);

    //         while (true) {
    //             await new Promise(resolve => setTimeout(resolve, 10000));

    //             const bnbOut = await getBnbOut(process.env.WBNB_ADDRESS, tokenAddr[0], buyTx.tokens);
    //             console.log(`BNB Out: ${(Number(bnbOut) / 10 ** 18).toFixed(2)}; BNB in: ${(Number(stringBuyAmount) / 10 ** 18).toFixed(2)}; RATIO: ${(Number(bnbOut) / Number(stringBuyAmount)).toFixed(2)}x`);

    //             if ((bnbOut > BigInt(stringBuyAmount) * BigInt(process.env.RATIO_TP)) || (bnbOut < BigInt(stringBuyAmount) * (BigInt(parseFloat(process.env.RATIO_SL)*100)) / (100n))) {
    //                 const sellTx = await swapTx(tokenAddr[0], process.env.WBNB_ADDRESS, 0, buyTx.tokens, false);
    //                 console.log(`\n✅ Sold for ${(Number(sellTx.tokens) / 10 ** 18).toFixed(2)} BNB at tx: ${sellTx.hash}`);
    //                 console.log(`FINAL RATIO: 🚀 ${(Number(sellTx.tokens) / Number(stringBuyAmount)).toFixed(2)}x`);
    //                 break;
    //             }
    //         }

    //     } catch (error) {
    //         console.log(`❌ Buy error: ${error.message}`);
    //     }
    // }
    // else {
    //     console.log(`TokenAddr length different from 1: ${tokenAddr}`);
    // }
}

client.addEventHandler(msgHandler, new NewMessage({ incoming: true, chats: process.env.CHANNELS.split(" ") }));

