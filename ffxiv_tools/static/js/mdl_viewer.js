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
        geometry.setIndex(new THREE.BufferAttribute(indices, 1));

        if (attrs.positions.length > 0 && attrs.positions[0].length > 0) {
            var positions = new Float32Array(attrs.positions.length * 3);
            for (var i = 0; i < attrs.positions.length; i++) {
                positions[3*i] = attrs.positions[i][0];
                positions[3*i+1] = attrs.positions[i][1];
                positions[3*i+2] = attrs.positions[i][2];
            }
            geometry.addAttribute('position', new THREE.BufferAttribute(positions, 3));
        }

        if (attrs.normals.length > 0 && attrs.normals[0].length > 0) {
            var normals = new Float32Array(attrs.normals.length * 3);
            for (var i = 0; i < attrs.normals.length; i++) {
                normals[3*i] = attrs.normals[i][0];
                normals[3*i+1] = attrs.normals[i][1];
                normals[3*i+2] = attrs.normals[i][2];
            }
            geometry.addAttribute('normal', new THREE.BufferAttribute(normals, 3));
        }

        if (attrs.colors.length > 0 && attrs.colors[0].length > 0) {
            var colors = new Float32Array(attrs.colors.length * 3);
            for (var i = 0; i < attrs.colors.length; i++) {
                colors[3*i] = attrs.colors[i][0];
                colors[3*i+1] = attrs.colors[i][1];
                colors[3*i+2] = attrs.colors[i][2];
            }
            geometry.addAttribute('color', new THREE.BufferAttribute(colors, 3));
        }

        if (attrs.uvs.length > 0 && attrs.uvs[0].length > 0) {
            var uvs = new Float32Array(attrs.uvs.length * 2);
            for (var i = 0; i < attrs.colors.length; i++) {
                uvs[2*i] = attrs.uvs[i][0];
                uvs[2*i+1] = attrs.uvs[i][1];
            }
            geometry.addAttribute('uv', new THREE.BufferAttribute(uvs, 2));
        }

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
