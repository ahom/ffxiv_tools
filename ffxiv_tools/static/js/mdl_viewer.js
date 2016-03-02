window.fetch('/model').then(function (data) {
    return data.json();
}).then(function (json) {
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

    var renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    var lod = json.lods[0];
    var meshes = [];
    
    lod.meshes.forEach(function (mesh) {
        var attrs = mesh.attributes;
        var geometry = new THREE.BufferGeometry();
        var indices = new Uint16Array(attrs.indices.length);

        for (var i = 0; i < indices.length; i++) {
            indices[i] = attrs.indices[i];
        }

        var positions = new Float32Array(attrs.positions.length * 3);

        for (var i = 0; i < attrs.positions.length; i++) {
            positions[3*i] = attrs.positions[i][0];
            positions[3*i+1] = attrs.positions[i][1];
            positions[3*i+2] = attrs.positions[i][2];
        }

        geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        geometry.addAttribute('position', new THREE.BufferAttribute(positions, 3));

        var material = new THREE.MeshBasicMaterial({color: 0xff0000});
        meshes.push(new THREE.Mesh(geometry, material));
    });

    camera.position.z = 5;

    meshes.forEach(function (mesh) {
        scene.add(mesh);
    });

    function render() {
        requestAnimationFrame(render);

        meshes.forEach(function (mesh) {
            mesh.rotation.x += 0.1;
            mesh.rotation.y += 0.1;
        });

        renderer.render(scene, camera);
    }
    render();
})
