#version 130
// -----------------------------------------------------------------
// DISPLACEMENT MAPPING VARIABLES
// -----------------------------------------------------------------

// Displacement map texture
// uniform sampler2D colormap;
uniform sampler2D heightmap;
uniform sampler2D normalmap;

uniform bool process_stimuli;
uniform bool per_pixel;

const float SCALE_FACTOR = 1.5;

// varying vec2 fragTexCoord;
// varying vec4 fragVertex;
varying vec3 fragNormal;
varying vec3 fragColor;

// -----------------------------------------------------------------
// LIGHTING VARIABLES
// -----------------------------------------------------------------

// Set the number of lights in the scene
// const int NUM_LIGHTS = 1;

// Variables passed to the shader from the main program
// Position of camera
// uniform vec3 camera_position;
// Position of the lights
// uniform vec3 light_position[NUM_LIGHTS];

// Variables that will be passed onto the Fragment Shader
// Normal for the vertex
// varying vec3 frag_normal;
// Vector from each of the vertices to the camera
// varying vec3 camera_vector;
// Vector from each of the vertices to the the light source
// varying vec3 light_vector[NUM_LIGHTS];
uniform vec3 light_direction;

// -----------------------------------------------------------------
// RGB TO GREYSCALE FUNCTIONS
// -----------------------------------------------------------------

/*
float convert_average(vec4 pixel) {
    return (pixel.r + pixel.g + pixel.b) / 3.0;
}
*/

/*
float convert_luminance(vec4 pixel) {
    return (0.30 * pixel.r) + (0.59 * pixel.g) + (0.11 * pixel.b);
}
*/

float convert_luminance(vec4 pixel) {
    return (0.2126 * pixel.r) + (0.7152 + pixel.g) + (0.0722 * pixel.b);
}

/*
float convert_desaturation(vec4 pixel) {
    float mx;
    float mn;

    mx = max(pixel.r, pixel.g);
    mx = max(mx, pixel.b);

    mn = min(pixel.r, pixel.g);
    mn = min(mn, pixel.b);
    return (mx + mn) / 2.0;
}
*/

// -----------------------------------------------------------------
// HANDLE NORMALS
// -----------------------------------------------------------------

vec3 get_normal(void) {
    // Get pixel values for TexCoord
    vec4 pixel = texture(normalmap, gl_TexCoord[0].xy);
    return vec3(pixel.r, pixel.g, pixel.b);
}


// -----------------------------------------------------------------
// HANDLE DISPLACEMENT MAPPING
// -----------------------------------------------------------------

vec4 displacement_mapping(void) { 
    vec4 pixel = texture(heightmap, gl_TexCoord[0].xy);
    float grey_value = convert_luminance(pixel);

    return vec4(gl_Normal * grey_value * SCALE_FACTOR, 0.0) + gl_Vertex;
}

// -----------------------------------------------------------------
// HANDLE LIGHTING
// -----------------------------------------------------------------

// vec4 lighting(vec4 coord)
// {
//     // Set the normal for the fragment shader
//     frag_normal = gl_Normal;

//     // Set the vector from the vertex to the camera
//     camera_vector = camera_position - coord.xyz;
//     // Set the vectors from the vertex to each light
//     for(int i = 0; i < NUM_LIGHTS; ++i)
//         light_vector[i] = light_position[i] - coord.xyz;
    
//     // Output the transformed vector
//     return coord;
// }

void directional_lighting(vec3 normal) {
    vec3 diffuse = vec3(1.0, 1.0, 1.0);

    float intensity = max(dot(normal, light_direction), 0.0);
    // // intensity = (intensity - 0.3) * 10.0;
    // if (intensity >= 0.45)
    //     fragColor = 1.0 * vec3(1.0, 0.0, 0.0);
    // else if (intensity >= 0.4)
    //     fragColor = 1.0 * vec3(0.0, 1.0, 0.0);
    // else if (intensity < 0.3)
    //     fragColor = 1.0 * vec3(0.0, 0.0, 1.0);
    // fragColor = normal;
    // fragColor = normal * 100.0;

    fragColor = intensity * diffuse;
}

// -----------------------------------------------------------------
// MAIN FUNCTION
// -----------------------------------------------------------------

void main(void) {
    gl_TexCoord[0].st = gl_MultiTexCoord0.st;
    // fragTexCoord = gl_TexCoord[0].st;
    vec4 fragVertex = displacement_mapping();
    fragNormal = get_normal();

    if (!per_pixel && process_stimuli)
        directional_lighting(fragNormal);
    gl_Position = gl_ModelViewProjectionMatrix * fragVertex;
}
