//import products from "./products.js";

const main = () => {
  //const relasiIdentity = products.relasiIdentity;
  //const productRecommendations = products.recommendation;
  let products = []
  const url = 'http://localhost:5000/recommendation';
  
  const getRecommendation = async (relasiId) => {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json'
      },
      method: 'POST',
      body: JSON.stringify({relasiId}),
    });
  
    const responseJson = await response.json();
    let relasiIdentity = responseJson.relasi;
    responseJson.recommendation.forEach(element => {
      products.push(element);
    });
  
    //RenderReccomendation();
    renderAllRecommendation(relasiIdentity, products);
  };

  // const getRecommendation = () => {
  //   renderAllRecommendation(relasiIdentity, productRecommendations);
  // };

  const renderAllRecommendation = (identity, products) => {
    const container = document.querySelector('.main-container');
    container.innerHTML = '';
    container.innerHTML += `
      <div class="flex" id="relasi-container"></div>
      <h1 class="label">Produk Rekomendasi</h1>
      <div class="grid-container"></div>
    `;
  
    const identityContainer = document.querySelector('#relasi-container');
    identityContainer.innerHTML = `
      <div id="location-section">
        <h1 class="location">Identitas</h1>
        <table>
          <tr>
            <th>Nama Relasi</th>
            <td>${identity[0]}</td>
          </tr>
          <tr>
            <th>Garis Lintang</th>
            <td>${identity[1]}</td>
          </tr>
          <tr>
            <th>Garis Bujur</th>
            <td>${identity[2]}</td>
          </tr>
          <tr>
            <th>Provinsi</th>
            <td>${identity[3]}</td>
          </tr>
        </table> 
      </div>
      <div id="condition-section">
        <h1 class="condition">Kondisi Lokasi</h1>
        <table>
          <tr>
            <th>Dominan Cuaca</th>
            <td>${identity[4]}</td>
          </tr>
          <tr>
            <th>Usia Mayoritas</th>
            <td>${identity[5]} tahun</td>
          </tr>
        </table>
      </div>
    `;
    
    const gridContainer = document.querySelector('.grid-container');
    for (const product of products) {
      const productElement = document.createElement('div');
      productElement.classList.add('grid-item');

      productElement.innerHTML += `
        <img src="./icon.png" alt="">
        <p class="rating"">${product[12]}</p>
        <div class="identity-content flex-column">
          <p class="title">${product[1]}</p>
          <p class="release-date">${product[3]}</p>
        </div>
        <div class="id-aaccess" id="${product[0]}"></div>
      `;

      gridContainer.appendChild(productElement);
      productElement.addEventListener('click', event => {
        const productId = event.target.id;

        detailProduct(productId);
      });
    };
  };

  const detailProduct = (productId) => {
    const product = findProduct(productId);
    const container = document.querySelector('main');
    container.innerHTML = '';
    container.innerHTML += `
      <form id="relasi-form">
        <label for="relasi">Nama Relasi:</label><br>
        <select id="relasi" name="relasi-select">
          <option value="relasi1">Relasi 1</option>
          <option value="relasi2">Relasi 2</option>
          <option value="relasi3">Relasi 3</option>
          <option value="relasi4">Relasi 4</option>
        </select>
        <button type="submit" id="submit-relasi-button">Cari Produk</button>
      </form>
      <div class="main-container"></div>
      <div id="product-section"></div>
    `;

    let weatherCondition;
    if (product[10] == 0) {
      weatherCondition = 'Dominan digunakan pada cuaca dingin';
    } else if (product[10] == 1) {
      weatherCondition = 'Digunakan pada cuaca dingin dan panas';
    } else {
      weatherCondition = 'Dominan digunakan pada cuaca panas';
    }

    let ageOfUser;
    if(product[11] == '[0]') {
      ageOfUser = 'Obat untuk anak-anak';
    } else if (product[11] == '[0,1]') {
      ageOfUser = 'Obat untuk anak-anak dan remaja';
    } else if (product[11] == '[2]') {
      ageOfUser = 'Obat untuk orang dewasa';
    } else {
      ageOfUser = 'Obat untuk anak-anak dan dewasa';
    }

    const detailContainer = document.querySelector('#product-section');
    detailContainer.innerHTML += `
      <h1 class="product label">Identitas Produk</h1>
      <p class="description">${product[6]}</p>
      <h1 class="dosage label">Dosis Penggunaan</h1>
      <p>${product[7]}</p>
      <div class="flex">
        <div id="indication">
          <h1 class="indication label">Indikasi dan Kegunaan</h1>
          <p>${product[5]}</p>
        </div>
        <div id="purpose">
          <h1 class="purpose label">Tujuan</h1>
          <p>${product[4]}</p>
        </div>
      </div>
      <h1 class="condition label">Hasil Analisis</h1>
      <table>
        <tr>
          <th>Poin hasil</th>
          <td>${product[12]}</td>
        </tr>
        <tr>
          <th>Kluster</th>
          <td>${product[9]}</td>
        </tr>
        <tr>
          <th>Kondisi Cuaca</th>
          <td>${weatherCondition}</td>
        </tr>
        <tr>
          <th>Umur Pengguna</th>
          <td>${ageOfUser}</td>
        </tr>
      </table>
    `;
  }

  const findProduct = (productId) => {
    let product = null;
    for (const element of products) {
      if (element[0] == productId);
      product = element;
    }

    return product;
  }

  const findRelasiButton = document.querySelector('#submit-relasi-button');
  findRelasiButton.addEventListener('click', event => {
    event.preventDefault();
    const form = new FormData(document.getElementById('relasi-form'))
    getRecommendation(parseInt(form.get('relasi-select')));
  })

};

export default main;
