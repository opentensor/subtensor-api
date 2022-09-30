const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: './index.js',
  mode: "production",
  target: 'node',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    clean: true,
  },
  resolve: {
    fallback: {
      assert: require.resolve("assert"),
      fs: false,
      path: require.resolve("path-browserify"),
      os: require.resolve("os-browserify/browser")
    },
  },
  plugins: [
    new webpack.optimize.LimitChunkCountPlugin({
        maxChunks: 1, // disable creating additional chunks
    })
  ],
};