<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<style>
/* Global CSS reset và base styles cho màn hình Tablet POS */
html, body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
  background-color: #f4f7f6;
  height: 100%;
}
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
* {
  box-sizing: border-box;
}
button {
  cursor: pointer;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
}
button:hover {
  opacity: 0.9;
}
input, select {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px 15px;
  outline: none;
}
input:focus, select:focus {
  border-color: #4a90e2;
}
</style>
