const   webpack = require('webpack');
const ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
    entry: {
        app: [
            "./src/jsx/app.jsx",
            "./sass/my_app_styles.scss"
        ]
    },
    output: {
        filename: "../my_flask_app/static/js/[name].js" /* "./build/bundle.js" */
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                query: {
                    presets: ['es2015', 'react']
                }
            },
            {
                test: /\.(sass|scss)$/,
                loader: ExtractTextPlugin.extract(['css-loader', 'sass-loader'])
            }
        ]
    },
    plugins: [
        new webpack.optimize.UglifyJsPlugin(),
        new ExtractTextPlugin({
            filename: "../my_flask_app/static/css/[name].css",
            allChunks: true
        })
    ]
};