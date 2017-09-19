Offline Tx Signer
==============

Meant for easy offline signing of BIP32 based bitcoin (or alt-coin) transactions, and developed in a way to be easily integrated with other software systems.  Integration is a simple matter developing two features – one to provide a JSON file of raw inputs / outputs that are awaiting to be signed, and another to import a JSON file of signed transactions and send them appropriately.

This supports BIP32 addresses, all formats of key indexes, multi-signature transactions, generation of both master and hardened child keys, and more.  It will also spend change during the signing process, meaning as long as the amount of inputs in the JSON file are of equal or greater value to the amount of outputs, all necessary transactions will be signed / generated.


## Raw Transaction Format

First requirement is to develop a feature within your software that will provide your users a JSON file of raw inputs / outputs that are awaiting to be signed.  This is meant for watch-only wallets or similar, meaning you should already have a database of unspent inputs.  Due to change, instead of using full raw transactions, the file format only requires a list of inputs and outputs.


##### Quick Example

```
{
“txfee_paidby”: “sender”, 
"change_addr_format": "3of5", 

"inputs": [
     { "input_id":"4",
        "amount":"0.20000000",
        "txid":"606c772eaaaf5e8456f9670251b52e97b8a8134d6f84c5a662807c6cd7e75ec9",
        "vout":"1",
        "sigscript":"76a9146f089bc9abc84550298dd547341c964a810248e788ac",
        "keyindex":"0\/13",
        "change_keyindex":"1\/14"
     }
],

"outputs": [
      { "output_id":"2",
        "amount":"0.10000000",
        "address":"mhCnq89xRnfmmBerVW7aN3cQG9KJr6mRF7"
      }
]
}
```


##### Settings

Settings that are available within the JSON file, but not required.  These allow you to do things such as define who pays the fee, the base tx fee, and more.

Variable | Required | Notes
-------- | -------- | -----
wallet_id | No | Any type of unique ID# or name for the wallet processing the funds.  If present, this variable will be included in the return file.
txfee_paidby | No | Can be either:  **sender**, **recipient**, or **site**.  Defaults to recipient.
txfee | No | The base tx fee to charge (per 1000 bytes)  Defaults to 0.0001
change_keyindex | No | Optional.  Default key index to use (eg. 1/43) for all change transactions generated during a batch signing.  Only used for outputs that do not have a *change_keyindex* defined.
public_prefix | No | Optional.  Only needed if processing an alt-coin that is NOT bitcoin.  This should be the two digit hexdecimal prefix for public keys (eg. bitcoin = 00)
private_prefix | No | Optional.  Only needed if processing an alt-coin that is NOT bitcoin.  This should be the two digit hexdecimal prefix for private keys (eg. bitcoin = 08).


##### Inputs

An array of all of the inputs to use.  The below table lists the variables allowed for each input:

Variable | Required | Notes
-------- | -------- | -----
input_id | No | Any unique ID# to identify the input being used.  This will be included in the return file, so you know to mark the input as spent.
amount | Yes | Amount of the input.
txid | Yes | Transaction hash of the input.
vout | Yes | Integer defining the vout of the input (ie. 0, 1, 2, etc.)
sigscript | Yes | Signature script of the input.  For multisig inputs, this is the full redeem script.
keyindex | Yes | Key index of the input (eg. 0/43), or whatever key index is used to generate the necessary child key using the BIP32 key that will be input during signing.


##### Outputs

An array of all of the outputs to that will be sent.  The below table lists the variables allowed for each output:

Variable | Required | Notes
-------- | -------- | -----
output_id | No | Any unique ID# to identify the output.  This will be included in the return file, so you know the transaction was signed / sent.
amount | No | Amount to send.  Required unless you're using the below 'recipients' field.
address | No | Address to send funds to.  Required unless you're using the below 'recipients' field.
recipients | No | Optional array of recipients, and is only required if you are sending to more than one address.  Each element within the array should be an array containing two elements (*amount* and *address*)
change_keyindex | No | Key index to use for any change left over from this input.  
change_address | No | Change address to be used.
change_sigscript | No | Change sigscript to use.



## Signed Transaction Format

Once you've imported the raw transaction file and have signed the transactions, you will receive another JSON file.  The second part of the integration requires development of a another function within your software system that will accept the signedtx.json file, and send all transactions within it.  This JSON file is formatted as show below.


##### Quick Example

```
{
“wallet_id”: “32”, 

"tx": [
     { "output_id":"2",
        "amount":"0.10000000",
        “to_address”:”mhCnq89xRnfmmBerVW7aN3cQG9KJr6mRF7”, 
        “txid”:”2dcbbd8a4db5e1f57ad187fd6e618c7c1d85305012e81e7f7a4ffcd36cc8fb23”,   
“hexcode”:”0100000001c95ee7d76c7c8062a6c5846f4d13a8b8972eb5510267f956845eafaa2e776c60010000006a47304402204e1c925b4837e2916b3103d9a07c222891ae4b20820e21c166fa53e39a3e67570220006a202df997b9807dba30b437a0347ba5f3218183d01d1da1f909cb9a43eded012102b6da885ec39f34d0e598e2da3c6bf4e0974c18cae168659e62c7f052b17584dcffffffff0280969800000000001976a9141280dd253638815278dae4752e05520eb08c11f688ac706f9800000000001976a914dd5a0e40a88e9a2cf91f797870dd6e0f27b8e9e288ac00000000”
     }
],

"spent_inputs": [
     { "input_id":"4",
        "amount":"0.20000000",
        "txid":"606c772eaaaf5e8456f9670251b52e97b8a8134d6f84c5a662807c6cd7e75ec9",
        "vout":"1",
        "sigscript":"76a9146f089bc9abc84550298dd547341c964a810248e788ac",
        "keyindex":"0\/13",
        "change_keyindex":"1\/14"
     }
],

"change_inputs": [
     { "input_id":"c1",
        "amount":"0.09990000",
        "txid":"2dcbbd8a4db5e1f57ad187fd6e618c7c1d85305012e81e7f7a4ffcd36cc8fb23",
        "vout":"1",
        "sigscript":"76a914dd5a0e40a88e9a2cf91f797870dd6e0f27b8e9e288ac",
        "keyindex":"1\/14",
        "change_keyindex":"1\/14"
     }
],
}
```

##### Tx

An array containing all of the signed transactions, including the full hexcode of each that needs to be broadcast to the blockchain.

Variable | Notes
-------- | -----
output_id | Only present if an output_id variable was defined within the raw transaction JSON file.  If so, this will be the output_id previously defined, allowing you to better track the transaction.
amount | Amount sent.
to_address | Address the amount was sent to.
txid | The ID# of the transaction, as it will appear in the blockchain.
hexcode | The full hexcode of the signed transaction, which needs to be broadcast to the blockchain.


##### Spent Inputs / Change Inputs

Two separate arrays containing all of the inputs that were spent, and all of the change inputs created during the signing process.  For the “spent_inputs” array, all variables are simply echoed from what was defined within the raw transaction file.  This helps you mark the inputs as spent within your own system.

For the “change_inputs” array, they are all newly generated inputs that you may want to add into your system, instead of waiting for them to be confirmed within the blockchain.  Please note, some of the change inputs might already be spent, and if so, will appear within the “spent_inputs” array as well.

Variable | Notes
-------- | -----
input_id | Unique ID# of the input.  If a change input, always in the format of cXX where XX  is a number that begins with 1, and increments by 1 for each change input.
amount | Amount of the input.
txid | Txid of the input.
vout | Vout of the input.
sigscript | Signature script of the input.
keyindex | Keyindex of the input.
change_keyindex | Change keyindex of the input.


