console.log("scripts.js!");

let images; // Variable globale pour stocker l'image
let flipped = false; // Variable pour suivre l'état de l'image (retournée ou non)

function toggleDropdown() {
  const dropdown = document.querySelector(".dropdown");

  if (dropdown) {
    dropdown.classList.toggle("show");
  } else {
    console.error("Élément '.dropdown' introuvable !");
  }

  // Basculer entre les états retourné et normal
  if (images) {
    flipped = !flipped; // Inverse l'état
    images.style.transform = flipped ? "scaleY(-1)" : "scaleY(1)"; // Applique la transformation en fonction de l'état
  } else {
    console.error("Élément '.image-database' introuvable !");
  }
}

function loadJsonAndUpdateDropdown() {
  const dropdown = document.querySelector(".dropdown");

  if (dropdown) {
    // Vider le contenu du dropdown avant de le mettre à jour
    dropdown.innerHTML = ''; // Cela efface toutes les options existantes à chaque fois

    // Utilisation de fetch pour charger le fichier JSON
    fetch(jsonUrl) // jsonUrl doit être défini dans ton HTML
      .then((response) => {
        if (!response.ok) {
          throw new Error("Erreur lors du chargement du fichier JSON");
        }
        return response.json();
      })
      .then((data) => {
        // Itérer sur chaque hyperviseur et afficher son hostname
        data.forEach((hyperviseur) => {
          const hostname = hyperviseur.hostname;
          const li = document.createElement("li");

          // Ajouter un gestionnaire d'événements au clic sur chaque hyperviseur
          li.innerHTML = `<a href="#">${hostname}</a>`;
          li.addEventListener('click', function() {
            createListVm(hyperviseur); // Créer la liste des machines virtuelles

            // Supprimer la classe 'selected' de tous les liens <a>
            const allLinks = document.querySelectorAll(".dropdown.show li a");
            allLinks.forEach(link => link.classList.remove("selected"));
        
            // Ajouter la classe 'selected' au lien <a> du <li> cliqué
            const link = this.querySelector("a");
            if (link) {
              link.classList.add("selected");
            }

          });

          dropdown.appendChild(li);
        });
      })
      .catch((error) => {
        console.error("Erreur : ", error);
      });
  } else {
    console.error("Élément '.dropdown' introuvable !");
  }
}

// Fonction pour créer la div list_vm dans le <main>
function createListVm(hyperviseur) {
  const main = document.querySelector("main");

  if (main) {
    const div = document.querySelector("#list_vm");

    // Générer la liste des machines virtuelles
    const vmList = hyperviseur.domains.map(domain => `
      <li class="vm-item" data-vm='${JSON.stringify(domain)}'>${domain.name}</li>
    `).join('');
  
    // Insérer les informations générales et la liste des VM dans le HTML
    div.innerHTML = `
      <h3>Virtual Machines:</h3>
      <ul>
        ${vmList}
      </ul>
      <h3>General Informations:</h3>
      <ul>
        <li><strong>URI:</strong> ${hyperviseur.uri}</li>
        <li><strong>Hostname:</strong> ${hyperviseur.hostname}</li>
        <li><strong>CPU Model:</strong> ${hyperviseur.cpu_model}</li>
        <li><strong>Memory Size:</strong> ${hyperviseur.memory_size_mb} MB</li>
        <li><strong>CPU Count:</strong> ${hyperviseur.cpu_count}</li>
        <li><strong>CPU Frequency:</strong> ${hyperviseur.cpu_frequency_mhz} MHz</li>
        <li><strong>NUMA Nodes:</strong> ${hyperviseur.numa_nodes}</li>
        <li><strong>CPU Sockets per Node:</strong> ${hyperviseur.cpu_sockets_per_node}</li>
        <li><strong>Cores per Socket:</strong> ${hyperviseur.cores_per_socket}</li>
        <li><strong>Threads per Core:</strong> ${hyperviseur.threads_per_core}</li>
      </ul>
    `;

    // Ajouter un écouteur de clic sur chaque élément <li> de la liste
    const vmItems = document.querySelectorAll("#list_vm .vm-item");
    vmItems.forEach(item => {
      item.addEventListener('click', function() {
        vmItems.forEach(vm => vm.classList.remove('selected'));
        item.classList.add('selected');
        const vmData = JSON.parse(item.getAttribute('data-vm')); // Récupérer les données de la VM
        updateOptionVm(vmData); // Passer les données de la VM à la fonction de mise à jour
      });
    });
  } else {
    console.error("Élément <main> introuvable !");
  }
}

// Fonction pour effacer et mettre à jour #option_vm avec les données de la VM
function updateOptionVm(vmData) {
  const optionVmDiv = document.querySelector("#option_vm");

  if (optionVmDiv) {
    // Vider le contenu de la div #option_vm
    optionVmDiv.innerHTML = '';

    // Créer un contenu structuré avec les données de la machine virtuelle
    optionVmDiv.innerHTML = `
      <strong>Start Virtual Machine</strong>
      <strong> Migrate Virtual Machine</strong>
      <h3>General Information:</h3>
      <p><strong>Name:</strong> ${vmData.name}</p>
      <p><strong>UUID:</strong> ${vmData.uuid}</p>
      <p><strong>State:</strong> ${vmData.state}</p>
      <p><strong>Max Memory:</strong> ${vmData.max_memory_kb / 1024} MB</p>
      <p><strong>Memory Used:</strong> ${vmData.memory_used_kb / 1024} MB</p>
      <p><strong>VCPU Count:</strong> ${vmData.vcpu_count}</p>
      <p><strong>CPU Time:</strong> ${vmData.cpu_time_ns / 1e9} seconds</p>
    `;
  } else {
    console.error("Élément #option_vm introuvable !");
  }
}

// S'assurer que le code s'exécute après que tout soit chargé
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM entièrement chargé et analysé");

  // Initialise `images` avec l'élément ayant la classe "image-database"
  images = document.querySelector(".image-database");

  if (images) {
    flipped = !flipped; // Inverse l'état
    images.style.transform = flipped ? "scaleY(-1)" : "scaleY(1)"; // Applique la transformation en fonction de l'état
  } else {
    console.error("Élément '.image-database' introuvable !");
  }

  // Ajout de l'écouteur de clic pour appeler toggleDropdown et charger le JSON
  const button = document.querySelector(".toggle-button");

  if (button) {
    button.addEventListener("click", () => {
      toggleDropdown();
      loadJsonAndUpdateDropdown();
    });
  } else {
    console.error("Bouton '.toggle-button' introuvable !");
  }

  const bouton1 = document.getElementById("button1");
  const form = document.getElementById("hypervisorForm");
  
  // Lorsque le bouton "Add Hypervisor" est cliqué, affichez ou cachez le formulaire
  bouton1.addEventListener("click", function () {
    // Si le formulaire est déjà visible, on le cache, sinon on l'affiche
    if (form.style.display === "none" || form.style.display === "") {
      form.style.display = "block";  // Afficher le formulaire
    } else {
      form.style.display = "none";   // Cacher le formulaire
    }
  });

  // Ajouter une gestion de la soumission du formulaire pour l'hyperviseur
  form.addEventListener("submit", function (e) {
    e.preventDefault(); // Empêcher l'envoi du formulaire pour le moment

    const hypervisorPath = document.getElementById("hypervisorPath").value;
    console.log("Chemin de l'hyperviseur:", hypervisorPath);

    // Vous pouvez ajouter ici du code pour traiter les données saisies, comme un appel API ou autre.

    // Après soumission, vous pouvez aussi cacher le formulaire à nouveau si nécessaire.
    form.style.display = "none"; // Cacher le formulaire après validation
  });

  // Fonction pour afficher/masquer le formulaire de création de VM
  document.getElementById("button2").addEventListener("click", function () {
    const form = document.getElementById("create-vm-form");
    if (form.style.display === "none" || form.style.display === "") {
      form.style.display = "block";  // Afficher le formulaire
    } else {
      form.style.display = "none";   // Cacher le formulaire
    }
    form.classList.toggle("active");

    const hypervisorSelect = document.getElementById("hypervisor-select");
    hypervisorSelect.innerHTML = ''; // Vider le menu déroulant avant de le remplir

    // Charger les hyperviseurs depuis le JSON et les ajouter au menu déroulant
    fetch(jsonUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Erreur lors du chargement du fichier JSON");
        }
        return response.json();
      })
      .then((data) => {
        data.forEach((hyperviseur) => {
          const option = document.createElement("option");
          option.value = hyperviseur.hostname;
          option.textContent = hyperviseur.hostname;
          hypervisorSelect.appendChild(option);
        });
      })
      .catch((error) => {
        console.error("Erreur de chargement des données : ", error);
      });
  });

  // Gérer la modification du nombre de vCPUs en fonction de l'hyperviseur sélectionné
  document.getElementById("hypervisor-select").addEventListener("change", function () {
    const selectedHypervisor = this.value;

    // Recharger les données JSON pour récupérer l'hyperviseur sélectionné
    fetch(jsonUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Erreur lors du chargement du fichier JSON");
        }
        return response.json();
      })
      .then((data) => {
        const hypervisor = data.find(h => h.hostname === selectedHypervisor);
        const vcpuInput = document.getElementById("vcpu-count");

        // Limiter les vCPUs à la capacité de l'hyperviseur sélectionné
        vcpuInput.setAttribute("max", hypervisor.cpu_count); // Définir la capacité max de vCPU
      })
      .catch((error) => {
        console.error("Erreur de chargement des données : ", error);
      });
  });

  // Soumettre le formulaire pour créer une machine virtuelle
  document.getElementById("vmForm").addEventListener("submit", function (e) {
    e.preventDefault(); // Empêcher la soumission du formulaire

    const hypervisor = document.getElementById("hypervisor-select").value;
    const maxMemory = document.getElementById("max-memory").value;
    const vcpuCount = document.getElementById("vcpu-count").value;
    const vmName = document.getElementById("vm-name").value;  // Récupérer le nom de la VM

    // Validation du nom de la VM
    if (!vmName) {
      alert("Veuillez entrer un nom pour la VM.");
      return; // Arrêter l'exécution si le nom de la VM est vide
    }

    console.log(`VM créée sur l'hyperviseur: ${hypervisor}`);
    console.log(`Nom de la VM: ${vmName}`);
    console.log(`Mémoire maximale: ${maxMemory} MB`);
    console.log(`Nombre de vCPU: ${vcpuCount}`);

    // Vous pouvez ajouter ici la logique pour envoyer ces données à un serveur ou effectuer une autre action
  });
});
