#version 130

// -----------------------------------------------------------------
// DISPLACEMENT MAPPING VARIABLES
// -----------------------------------------------------------------

// varying vec2 fragTexCoord;
// varying vec4 fragVertex;
varying vec3 fragNormal;
varying vec3 fragColor;

// Original (unblurred) image texture
uniform sampler2D colormap;

// -----------------------------------------------------------------
// LIGHTING VARIABLES
// -----------------------------------------------------------------

// Set the number of lights in the scene
// const int NUM_LIGHTS = 1;
// Set the factor to raise the lighting effect by
// const float FACTOR = 1.7;

// Variables passed to the shader from the main program
// Color setting of each light source
// uniform vec3 light_color[NUM_LIGHTS];

// Variables received from the Vertex Shader
// Normal for the vertex
// varying vec3 frag_normal;
// Vector from each of the vertices to the camera
// varying vec3 camera_vector;
// Vector from each of the vertices to the the light source
// varying vec3 light_vector[NUM_LIGHTS];
uniform vec3 light_direction;

// Ambient light values
const vec3 AMBIENT = vec3(0.0, 0.0, 0.0);
// Maximum distance at which the lighting has an effect
// const float MAX_DIST = 2.5;
// const float MAX_DIST_SQUARED = MAX_DIST * MAX_DIST;

// -----------------------------------------------------------------
// ENABLING BOOLEAN VARIABLES
// -----------------------------------------------------------------

// Boolean enabling the fragment shader to run
uniform bool process_stimuli;
uniform bool per_pixel;


// -----------------------------------------------------------------
// HANDLE DISPLACEMENT MAPPING
// -----------------------------------------------------------------

vec4 color_mapping(void) {
    return texture2D(colormap, gl_TexCoord[0].st);
}

// -----------------------------------------------------------------
// HANDLE LIGHTING
// -----------------------------------------------------------------

// vec4 lighting(void) {
//     // Initialize diffuse/specular lighting
//     vec3 diffuse = vec3(0.0, 0.0, 0.0);
//     vec3 specular = vec3(0.0, 0.0, 0.0);

//     // Normalize the fragment normal and camera direction
//     vec3 normal = normalize(frag_normal);
//     vec3 camera_direction = normalize(camera_vector);
    
//     // Loop through each light
//     for(int i = 0; i < NUM_LIGHTS; ++i)
//     {
//         // Calculate distance between 0.0 and 1.0
//         float dist = min(dot(light_vector[i], light_vector[i]), MAX_DIST_SQUARED) / MAX_DIST_SQUARED;
//         float dist_factor = 1.0 - dist;

//         // Handle diffuse lighting
//         vec3 light_direction = normalize(light_vector[i]);
//         float diffuse_dot = dot(normal, light_direction);
//         diffuse += light_color[i] * clamp(diffuse_dot, 0.0, 1.0) * dist_factor;
        
//         // Handle specular lighting
//         vec3 half_angle = normalize(camera_direction + light_direction);
//         vec3 specular_color = min(light_color[i] + 0.5, 1.0);
//         float specular_dot = dot(normal, half_angle);
//         specular += specular_color * pow(clamp(specular_dot, 0.0, 1.0), 60.0) * dist_factor;
//     }
    
//     vec4 sample = vec4(1.0, 1.0, 1.0, 1.0);
//     vec4 result = vec4(clamp(sample.rgb * (diffuse + AMBIENT), 0.0, 1.0), sample.a);
//     // Multiply it with FACTOR to increase the effect
//     return result * FACTOR;
// }

vec3 directional_lighting(void) {
    // float pf;

    // vec3 specular = vec3(0.0, 0.0, 0.0);
    vec3 diffuse = vec3(1.0, 1.0, 1.0);
    vec3 color = AMBIENT;

    // vec3 normal = get_normal();
    // float intensity = fragNormal.z;
    float intensity = max(dot(fragNormal, light_direction), 0.0);
    // intensity = pow(intensity, 2.0);
    // vec3 camera_direction = normalize(camera_vector);
    // vec3 half_vector = normalize(camera_direction + light_direction);
    // float intspec = max(dot(fragNormal, half_vector), 0.0);

    // If the vertex is lit compute the specular color
    // if (intensity >= 0.7)
        // intensity = 1.6;

    // if (intensity < 0.5)
        // intensity = 1.0;
    // else
        // intensity = 0.0;

    // if (intensity > 0.7)
    //     intensity = 0.0;
    // else
    //     intensity = 1.0;

    color += diffuse * intensity;
    // return normalize(fragNormal);
    // color += specular * pf;
    return color;
}

// -----------------------------------------------------------------
// MAIN FUNCTION
// -----------------------------------------------------------------

void main(void) {
    if (process_stimuli) {
        vec4 tex_color = color_mapping();
        if (per_pixel) {
            vec3 l_color = directional_lighting();
            gl_FragColor = vec4(tex_color.rgb * l_color, tex_color.a);
        } else
            gl_FragColor = vec4(tex_color.rgb * fragColor, tex_color.a);
        // float l_color = directional_lighting();
        // vec3 normal = get_normal();


        // vec3 l_color = directional_lighting();
        // gl_FragColor = vec4(tex_color.rgb * l_color, tex_color.a);
    }
    else {
        gl_FragColor = color_mapping();
    }
}
