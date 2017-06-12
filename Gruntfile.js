// grunt wrapper
module.exports = function(grunt){
    //load grunt modules by load-grunt-tasks automatically
    require('load-grunt-tasks')(grunt);
    // use directory definition in .yml
    var config = grunt.file.readYAML('Gruntfile.yml');

    grunt.initConfig({
        sass: {
            dist: {
                src: config.scssDir+'style.scss',
                dest: config.cssDir+'style.css'
            }
        },
        watch: {
            sass: {
                files: config.scssDir+'**/*.scss',
                tasks: ['sass']
            }
        },

    });

    // register task
    grunt.registerTask('default',[
        'sass',
        'watch'
    ]);
};

