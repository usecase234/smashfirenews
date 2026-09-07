<?php
/**
 * Plugin Name: Smashfire PR
 * Description: AI newsroom intake and editorial queue. Thin client for the
 *              independently-deployed Smashfire PR Hub — no LLM provider
 *              credentials ever live in this plugin.
 * Version: 0.0.1
 * Requires PHP: 8.1
 *
 * Phase 3: submission vertical slice (public intake, Pre-Writer/Finished
 * Drafts queues, publish-to-WordPress). See
 * docs/Smashfire_PR_Starting_Build_Plan.md for the phase sequence.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // No direct access.
}

define( 'SMASHFIRE_PR_VERSION', '0.0.1' );
define( 'SMASHFIRE_PR_DIR', plugin_dir_path( __FILE__ ) );
define( 'SMASHFIRE_PR_URL', plugin_dir_url( __FILE__ ) );

require_once SMASHFIRE_PR_DIR . 'includes/class-hub-client.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-admin-menu.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-post-types.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-asset-table.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-rest-routes.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-publisher.php';
require_once SMASHFIRE_PR_DIR . 'includes/class-public-submission.php';

Smashfire_PR_Asset_Table::register_activation_hook( __FILE__ );

/**
 * Boot the plugin. Phase 3 adds the submission vertical slice: the public
 * intake page, the admin REST proxy the Incoming/Drafts screens call, and
 * the publish action that turns a Hub draft into a real WordPress post.
 */
function smashfire_pr_bootstrap(): void {
	Smashfire_PR_Admin_Menu::register();
	Smashfire_PR_Post_Types::register();
	Smashfire_PR_Rest_Routes::register();
	Smashfire_PR_Public_Submission::register();
}
add_action( 'plugins_loaded', 'smashfire_pr_bootstrap' );
